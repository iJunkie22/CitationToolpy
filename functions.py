from __future__ import unicode_literals, print_function
import platform
import subprocess
import wx.richtext
from wx import TextEntry, FONTSTYLE_ITALIC
from collections import namedtuple

Mediums = namedtuple('Mediums', ('Undefined', 'Book', 'eBook', 'Wiki'))((-1, 0, 1, 2))


class MacStuff:
    isMac = unicode(platform.system()) in ('Darwin', 'Linux')

    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    class MacClipboard:

        def __init__(self, *args, **kwargs):
            raise NotImplementedError

        @staticmethod
        def copy(text_to_copy):
            p1 = subprocess.Popen("env pbcopy -pboard general -Prefer rtf",
                                  stdin=subprocess.PIPE, shell=True)
            stdo1, stde1 = p1.communicate(text_to_copy)
            p1.wait()
            return p1.returncode

        @staticmethod
        def paste():
            stdo2 = subprocess.check_output("env pbpaste -pboard general", shell=True)
            return stdo2

        @staticmethod
        def inspect(text_to_copy):
            p1 = subprocess.Popen("env textutil -info -stdin",
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
            stdo1, stde1 = p1.communicate(text_to_copy)
            return stdo1

        @staticmethod
        def convert(text_to_copy):
            p1 = subprocess.Popen("env textutil -convert rtf -stdin -stdout",
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
            stdo1, stde1 = p1.communicate(text_to_copy)
            return stdo1


class RtfString(object):
    def __init__(self):
        self.raw_rtf = br'{\rtf1\ansi\ansicpg1252\cocoartf1348\cocoasubrtf170'
        self.set_font()
        self.finish_init()
        self._is_bolded = False
        self._is_italicized = False
        self._is_underlined = False

    def _save_style_state(self):
        return self._is_bolded, self._is_italicized, self._is_underlined

    def _restore_style_state(self, args):
        assert len(args) == 3
        self.set_bold(args[0])
        self.set_italics(args[1])
        self.set_underline(args[2])

    def set_font(self, font_name=br'Helvetica'):
        self.raw_rtf += br'{\fonttbl\f0\fswiss\fcharset0 ' + font_name + br';}'

    def finish_init(self):
        self.raw_rtf += br'{\colortbl;\red255\green255\blue255;}' + \
                        br'\margl1440\margr1440\vieww10800\viewh8400\viewkind0\pard' + \
                        br'\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640' + \
                        br'\pardirnatural\f0'

    def bold_on(self):
        if not self._is_bolded:
            self._is_bolded = True
            self.raw_rtf += br'\b '

    def bold_off(self):
        if self._is_bolded:
            self._is_bolded = False
            self.raw_rtf += br'\b0 '

    def set_bold(self, should_bold=True):
        assert isinstance(should_bold, bool)
        if should_bold:
            self.bold_on()
        else:
            self.bold_off()

    def italics_on(self):
        if not self._is_italicized:
            self._is_italicized = True
            self.raw_rtf += br'\i '

    def italics_off(self):
        if self._is_italicized:
            self._is_italicized = False
            self.raw_rtf += br'\i0 '

    def set_italics(self, should_italicize=True):
        assert isinstance(should_italicize, bool)
        if should_italicize:
            self.italics_on()
        else:
            self.italics_off()

    def underline_on(self):
        if not self._is_underlined:
            self._is_underlined = True
            self.raw_rtf += br'\ul '

    def underline_off(self):
        if self._is_underlined:
            self._is_underlined = False
            self.raw_rtf += br'\ulnone '

    def set_underline(self, should_underline=True):
        assert isinstance(should_underline, bool)
        if should_underline:
            self.underline_on()
        else:
            self.underline_off()

    def export(self):
        return self.raw_rtf + br'}'

    def append_text(self, input_text):
        self.raw_rtf += input_text

    def append_styled_text(self, input_text2, style_dict):
        assert isinstance(style_dict, dict)
        style_backup = self._save_style_state()

        if 'bold' in style_dict.keys():
            self.set_bold(style_dict['bold'])

        if 'italics' in style_dict.keys():
            self.set_italics(style_dict['italics'])

        if 'underline' in style_dict.keys():
            self.set_underline(style_dict['underline'])

        self.append_text(input_text2)
        self._restore_style_state(style_backup)

    def swrite(self, input_text3, style_str):
        """

        :param input_text3:
        :param style_str: BIU (uppercase = on, lowercase = off)
        :return:
        """
        s_dict = {}
        f_style_str = unicode(style_str)
        if 'B' in f_style_str:
            s_dict['bold'] = True
        elif 'b' in f_style_str:
            s_dict['bold'] = False

        if 'I' in f_style_str:
            s_dict['italics'] = True
        elif 'i' in f_style_str:
            s_dict['italics'] = False

        if 'U' in f_style_str:
            s_dict['underline'] = True
        elif 'u' in f_style_str:
            s_dict['underline'] = False

        self.append_styled_text(input_text3, s_dict)


class FieldOps:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def cap_letter(lc_str, cap_pos):
        s1 = s2 = s3 = ""
        lc_len = len(lc_str)

        if lc_len == 0:
            return ""  # return an empty string for an empty string

        else:  # the string isnt empty
            s1 = lc_str[0:cap_pos]
            s2 = lc_str[cap_pos:cap_pos + 1].upper()

            if cap_pos + 1 < lc_len:
                s3 = lc_str[cap_pos + 1:]

            else:
                s3 = ""

            return s1 + s2 + s3

    @staticmethod
    def italicize_text_range(rtb, i_start, i_stop):
        assert isinstance(rtb, wx.richtext.RichTextParagraphLayoutBox)
        targ_range = wx.richtext.RichTextRange(i_start, i_stop)
        old_attrs = rtb.GetAttributes()
        assert isinstance(old_attrs, wx.richtext.RichTextAttr)
        new_attrs = old_attrs.Copy()
        assert isinstance(new_attrs, wx.richtext.RichTextAttr)
        new_attrs.SetFontStyle(FONTSTYLE_ITALIC)
        rtb.SetStyle(targ_range, new_attrs)
        return True

    @staticmethod
    def append_as_italic(rtb2, i_str):
        assert isinstance(rtb2, wx.richtext.RichTextParagraphLayoutBox)
        i_str_len = len(i_str)  # Insertion length
        pre_len = len(rtb2.GetText())  # Insertion start position
        rtb2.AddParagraph(i_str)
        return FieldOps.italicize_text_range(rtb2, pre_len, i_str_len)

    @staticmethod
    def get_field_text(tb_in, default_text):
        assert isinstance(tb_in, TextEntry)
        if tb_in.IsEmpty():
            return default_text
        else:
            return tb_in.GetValue()

    @staticmethod
    def get_initials(name_str):
        assert isinstance(name_str, unicode)
        results = [""]
        if len(name_str) == 0:
            return results  # return an empty string for an empty string

        else:
            return list(name[0:1].upper() for name in name_str.split())


# MacStuff.MacClipboard.copy("Hello, World!")

if __name__ == '__main__':
    rtf_str2 = RtfString()


    def way1():
        rtf_str2.append_styled_text(br'this is bold', {'bold': True})
        rtf_str2.append_styled_text(br' and this is italicized', {'italics': True})
        rtf_str2.append_styled_text(br' and this is underlined!', {'underline': True})
        rtf_str2.append_styled_text(br'...And this is all 3!', {'bold': True, 'italics': True, 'underline': True})


    def way2():
        rtf_str2.swrite(br'this is bold', 'B')
        rtf_str2.swrite(br' and this is italicized', 'I')
        rtf_str2.swrite(br' and this is underlined!', 'U')
        rtf_str2.swrite(br'...And this is all 3 dude!', 'BIU')

    way2()
    # print(MacStuff.MacClipboard.copy(MacStuff.MacClipboard.convert(rtf_str2.export())))
    print(MacStuff.MacClipboard.copy(rtf_str2.export()))
    print(MacStuff.MacClipboard.convert(rtf_str2.export()))
    print(MacStuff.MacClipboard.paste())

    # Note that the clipboard contents will only show up in rich editors (like TextEdit)
    # print(MacStuff.MacClipboard.paste())
