import re
import logging
import string

log = logging.getLogger("text_prep")

# define punctuation chars !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~  plus some unicode punct ¿؟¡¢
expanded_punct = string.punctuation + chr(191) + chr(1567) + chr(161) + chr(162)
# £¥©®§
expanded_punct = expanded_punct + chr(163) + chr(165) + chr(169) + chr(174) + chr(167)
#  unicode additions (found with https://unicode-table.com/en/blocks/general-punctuation/)
#     this picks up en-dash, em-dash and punctuation seen in (at least) Russian
for i in range(8192, 8303):
    if i == 8293:  # unused
        continue
    expanded_punct = expanded_punct + chr(i)

def extract_tokens(str_content):
    """
    Clean given string and return the cleaned list of tokens.
    Punctuation, excess whitespace, control chars, funny stuff, is removed.
    :param str_content: raw string
    :return: token list, preserving order from document.
    """
    # convert control and EOL chars to space
    str_content = re.sub(r'[\x00-\x1F]+', ' ', str_content)
    # split by whitespace
    tokens = str_content.split()

    ttable = str.maketrans('', '', expanded_punct)
    tokens = [w.translate(ttable) for w in tokens]
    return tokens


def basename(fpath):
    offset_slash = fpath.rfind("/")
    if offset_slash >= 0:
        fpath = fpath[offset_slash + 1:]
    return fpath


def dirname(fpath):
    offset_slash = fpath.rfind("/")
    if offset_slash <= 0:
        return "."
    fpath = fpath[:offset_slash]
    return fpath


def trim_tokens(file_token_list, max_tokens):
    """
    If given list has more than given max_tokens, return an even split between the head and tail of the
    list so that total number of tokens is max_tokens.
    :param file_token_list: the tokens to check.
    :param max_tokens: max number of tokens to return as a list.
    :return:
    """
    ntokens = len(file_token_list)
    if ntokens > max_tokens:
        cut_out = ntokens - max_tokens
        front_end_offset = int(max_tokens/2)
        back_begin_offset = front_end_offset + cut_out
        file_token_list = file_token_list[:front_end_offset] + file_token_list[back_begin_offset:]
    return file_token_list

