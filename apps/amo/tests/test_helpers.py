from datetime import datetime

from nose.tools import eq_
from mock import Mock, patch

import jingo
import test_utils

import amo
from amo import urlresolvers


def render(s, context={}):
    t = jingo.env.from_string(s)
    return t.render(**context)


def test_page_title():
    request = Mock()
    request.APP = amo.THUNDERBIRD
    title = 'Oh hai!'
    s = render('{{ page_title("%s") }}' % title, {'request': request})
    eq_(s, '%s :: Add-ons for Thunderbird' % title)

    # pages without app should default to Firefox
    request.APP = None
    s = render('{{ page_title("%s") }}' % title, {'request': request})
    eq_(s, '%s :: Add-ons for Firefox' % title)


@patch('amo.helpers.urlresolvers.reverse')
def test_url(mock_reverse):
    render('{{ url("viewname", 1, z=2) }}')
    mock_reverse.assert_called_with('viewname', args=(1,), kwargs={'z': 2})


def test_urlparams():
    url = '/en-US/firefox/themes/category'
    c = {'base': url,
         'base_frag': url + '#hash',
         'base_query': url + '?x=y',
         'sort': 'name', 'frag': 'frag'}

    # Adding a query.
    s = render('{{ base_frag|urlparams(sort=sort) }}', c)
    eq_(s, '%s?sort=name#hash' % url)

    # Adding a fragment.
    s = render('{{ base|urlparams(frag) }}', c)
    eq_(s, '%s#frag' % url)

    # Replacing a fragment.
    s = render('{{ base_frag|urlparams(frag) }}', c)
    eq_(s, '%s#frag' % url)

    # Adding query and fragment.
    s = render('{{ base_frag|urlparams(frag, sort=sort) }}', c)
    eq_(s, '%s?sort=name#frag' % url)

    # Adding query with existing params.
    s = render('{{ base_query|urlparams(frag, sort=sort) }}', c)
    eq_(s, '%s?sort=name&x=y#frag' % url)

    # Replacing a query param.
    s = render('{{ base_query|urlparams(frag, x="z") }}', c)
    eq_(s, '%s?x=z#frag' % url)

    # Params with value of None get dropped.
    s = render('{{ base|urlparams(sort=None) }}', c)
    eq_(s, url)


def test_isotime():
    time = datetime(2009, 12, 25, 10, 11, 12)
    s = render('{{ d|isotime }}', {'d': time})
    eq_(s, '2009-12-25 10:11:12')


def test_locale_url():
    rf = test_utils.RequestFactory()
    request = rf.get('/de', SCRIPT_NAME='/z')
    prefixer = urlresolvers.Prefixer(request)
    urlresolvers.set_url_prefix(prefixer)
    s = render('{{ locale_url("mobile") }}')
    eq_(s, '/z/de/mobile')
