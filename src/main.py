#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 13:49:20 2019

@author: user
"""
import os

from bokeh.plotting import figure
from bokeh.events import Tap, ButtonClick

from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, Button
from bokeh.io import curdoc
from bokeh.models.glyphs import ImageURL

import itertools
import time
import random
import string

from pdfrw import PdfReader, PdfWriter, PageMerge
from wand.image import Image

path = os.path.dirname(__file__)

STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")

class PdfFile():

    def __init__(self):

        files = list({f for f in os.listdir(os.path.join(STATIC_PATH, 'input_pdf'))
                     if os.path.isfile(os.path.join(STATIC_PATH, 'input_pdf', f))
                     if f.endswith('.pdf')
                     and not f.endswith('signed.pdf')})[0]

        self.target_doc = os.path.join(STATIC_PATH, 'input_pdf', files)

        self.init_input()

        self.outfn = os.path.join(STATIC_PATH, 'input_pdf',
                                  files.replace('.pdf', '_signed.pdf'))

        self.current_page = 0

        self.use_built_as_preview = False

    def init_input(self):

        self.trailer = PdfReader(self.target_doc)
        self.npages = len(self.trailer.pages)


    def switch_preview_source(self):

        self.use_built_as_preview = True

    def next_page(self):

        self.current_page += 1
        self.page_to_gif()

    def prev_page(self):

        self.current_page -= 1
        self.page_to_gif()

    def page_to_gif(self):

        self._page_to_gif(self.current_page)

    def _page_to_gif(self, pagenum):

        tgt_fn = self.outfn if self.use_built_as_preview else self.target_doc

        with Image(filename="{}[{}]".format(tgt_fn, pagenum),
                   resolution=100) as img:
            fn = random.choices(string.ascii_uppercase, k=5)
            fn = 'temp%s.gif'%''.join(fn)
            path = os.path.join(STATIC_PATH, fn)
            print('self.current_gif', path)
            img.save(filename=path)

        self.current_gif = fn


class Signature():

    def __init__(self, npages, scale=0.3):

        self.scale = scale

        self.sign_doc = os.path.join(STATIC_PATH, 'signature', 'signature.pdf')

        self.sign_trailer = PdfReader(self.sign_doc)

        self.date_pdf = self.get_date(self.select_date_files())

        self.init_locations(npages)

        self.sign_page = self.sign_trailer.pages[0]


        # bool alternating between date and signature selection
        self.select_date = False

    def switch_date_signature(self):

        self.select_date = bool(1 - self.select_date)


    def set_location(self, npage, xy):

        sign_date = 1 if self.select_date else 0

        self.locations[npage][sign_date] = xy

        self.switch_date_signature()

    def init_locations(self, npages):
        '''
        a dictionary with signature and date locations for each page
        '''

        self.locations = {ip: [(None, None), (None, None)] for ip in range(npages)}

    def select_date_files(self):


        files = {f for f in os.listdir(os.path.join(STATIC_PATH, 'numbers'))
                     if os.path.isfile(os.path.join(STATIC_PATH, 'numbers', f))}

        files_0 = {c: list(f for f in files if f.startswith(c))
                   for c in list(map(str, range(10))) + ['s']}

        date_str = time.strftime('%ds%ms%Y')

        d = date_str[0]

        files = files_0.copy()

        file_slct = []
        for d in date_str:
            if not files[d]:
                files[d] = [f for f in files_0[d]]

            file_slct.append(files[d].pop(0))

        return file_slct

    def get_date(self, date_filenames):

        date_pages = [PageMerge().add(PdfReader(os.path.join(STATIC_PATH, 'numbers', c)).pages[0])[0]
                      for c in date_filenames]

        return date_pages

    def date_scale_and_locate(self, xy, page_w, page_h):

        date_share_x, date_share_y = xy

        # can't copy due to NoneType issue, and need to copy to get different
        # pages
        date_pdf = self.get_date(self.select_date_files())

        for date in date_pdf:
            date.scale((self.scale) * page_w / 12 / date.w)

            # y: all chars aligned in the middle
            date.y = page_h * date_share_y - 0.5 * date.h

        date_pdf[0].x = page_w * date_share_x

        cum_x = date_pdf[0].x + date_pdf[0].w
        for date in date_pdf[1:]:

            date.x = cum_x
            cum_x += date.w

        return date_pdf

    def sign_scale_and_locate(self, xy, page_w, page_h):

        sign_share_x, sign_share_y = xy

        sign_pdf = PageMerge().add(self.sign_page.copy())[0]
        sign_pdf.scale((self.scale) * page_w / sign_pdf.w)
        sign_pdf.y = page_h * sign_share_y - 0.5 * sign_pdf.h
        sign_pdf.x = page_w * sign_share_x

        return sign_pdf


class PdfBuilder():

    def __init__(self, pdffile, signature):

        self.pdffile = pdffile
        self.signature = signature

    def add_signature(self, xy, page, page_w, page_h):
        print('calling sign_scale_and_locate')

        sign_pdf = self.signature.sign_scale_and_locate(xy, page_w, page_h)

        print('calling merging page')
        PageMerge(page).add(sign_pdf, prepend=False).render()


    def add_date(self, xy, page, page_w, page_h):

        print('calling date_scale_and_locate')
        date_pdf = self.signature.date_scale_and_locate(xy, page_w, page_h)

        for date in date_pdf:
            PageMerge(page).add(date, prepend=False).render()

    def build(self):

        self.pdffile.init_input()

        print('in build')
        for pagenum, page in enumerate(self.pdffile.trailer.pages, 0):

            mbox = tuple(float(x) for x in page.MediaBox)

            page_x, page_y, page_x1, page_y1 = mbox
            page_w = page_x1 - page_x
            page_h = page_y1 - page_y

            xy_sign = self.signature.locations[pagenum][0]
            xy_date = self.signature.locations[pagenum][1]

            if xy_sign[0]:
                self.add_signature(xy_sign, page, page_w, page_h)

            if xy_date[0]:
                self.add_date(xy_date, page, page_w, page_h)

        # Write out the destination file
        PdfWriter(self.pdffile.outfn, trailer=self.pdffile.trailer).write()


pdff = PdfFile()
pdff.page_to_gif()

sgnt = Signature(pdff.npages)

pdfbld = PdfBuilder(pdff, sgnt)


data_0 = dict(x_sign=[None], y_sign=[None], x_date=[None], y_date=[None])
source = ColumnDataSource(data=data_0)

def set_source(xy=None):
    print('set_source:', xy)

    if not xy:
        # reset
        source.data = data_0
    elif isinstance(xy, tuple):
        # update from selection
        x, y = xy
        if not sgnt.select_date:
            source.data.update(dict(x_sign=[x], y_sign=[y]))
        else:
            source.data.update(dict(x_date=[x], y_date=[y]))

    elif isinstance(xy, list):
        # reset to saved values
        source.data = dict(zip(source.data.keys(),
                               [[x] for x in itertools.chain.from_iterable(xy)]
                               ))

def make_title(p):

    p.title.text = "Page {}/{}".format(pdff.current_page + 1, pdff.npages)
    p.title.align = "left"

def get_coords(event):
    # save location in sgnt
    sgnt.set_location(pdff.current_page, (event.x, event.y))
    print(sgnt.locations)
    # update plot
    set_source((event.x, event.y))

p = figure(x_range=(0, 1), y_range=(0, 1),
           width=300, height=int(300 * 1.41421))
make_title(p)

def url_formatter(fn):
    return os.path.join(os.path.basename(os.path.dirname(__file__)), "static", fn)

url = url_formatter(pdff.current_gif)

im_source = ColumnDataSource(dict(url = [url]))

image1 = ImageURL(url="url", x=0, y=1, w=1, h=1)
p.add_glyph(im_source, image1)

p.on_event(Tap, get_coords)
p.circle('x_sign', 'y_sign', source=source, color='red')#show(p)
p.circle('x_date', 'y_date', source=source, color='blue')#show(p)


def page_change():
    im_source.data = {'url': [url_formatter(pdff.current_gif)]}
    set_source(sgnt.locations[pdff.current_page])
    make_title(p)

def do_next_page(event):
    pdff.next_page()
    page_change()

def do_prev_page(event):
    pdff.prev_page()
    page_change()

def do_build(even):
    pdfbld.build()
    pdff.switch_preview_source()

    pdff.page_to_gif()
    im_source.data = {'url': [url_formatter(pdff.current_gif)]}

button_next_page = Button(label="Next page")
button_next_page.on_event(ButtonClick, do_next_page)
button_prev_page = Button(label="Previous page")
button_prev_page.on_event(ButtonClick, do_prev_page)

button_build = Button(label="Build")
button_build.on_event(ButtonClick, do_build)


l = layout([
    [p],
    [button_next_page],
    [button_prev_page],
    [button_build]
], sizing_mode='fixed')

curdoc().add_root(l)
curdoc().title = "Sign PDF"




# %%