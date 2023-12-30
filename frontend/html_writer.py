# -*- coding: utf-8 -*-
from flask import request
from datetime import datetime
from urllib.parse import quote

from frontend.localizer import Localizer
from frontend.models import *

POSTS_PER_PAGE = 250
USER_LIST = 500


class HTMLWriter:
    def __init__(self):
        self.localizer = Localizer("cz")
        self.author = request.args.get('a', '')
        self.search = request.args.get('s', '')
        self.search_from = request.args.get('f', '')
        self.search_to = request.args.get('t', '')
        self.order = request.args.get('o', '')

        # Default to ordering by date
        if not self.order in set(['n', 'f']):
            self.order = 'n'

        try:
            self.page = int(request.args.get('p', '1'))
            if self.page < 1:
                self.page = 1
        except ValueError:
            self.page = 1
        self.localizer.addPageVariables(self.author, self.search, self.search_from, self.search_to, self.order, self.page)

        # Setting css class
        if self.order == 'n':
            label = "%(newest-label)s" % self.localizer.getDictionary()
            link = """<a href="/?a=%(author-quoted)s&s=%(search-quoted)s&p=1&f=%(search_from)s&t=%(search_to)s&o=f">%(funniest-label)s</a>""" % self.localizer.getDictionary()
            self.localizer.set("active-newest", "active")
            self.localizer.set("active-funniest", "")
            self.localizer.set("newest-tab", label)
            self.localizer.set("funniest-tab", link)
        elif self.order == 'f':
            label = "%(funniest-label)s" % self.localizer.getDictionary()
            link = """<a href="/?a=%(author-quoted)s&s=%(search-quoted)s&p=1&f=%(search_from)s&t=%(search_to)s&o=n">%(newest-label)s</a>""" % self.localizer.getDictionary()
            self.localizer.set("active-newest", "")
            self.localizer.set("active-funniest", "active")
            self.localizer.set("newest-tab", link)
            self.localizer.set("funniest-tab", label)

    def get_header(self):
        return """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<title>%(web-name)s</title>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<meta name="robots" content="noindex,nofollow">
<link rel="shortcut icon" href="/res/img/favicon.ico" />
<link rel="icon" type="image/x-icon" href="/res/img/favicon.ico" />
<link rel="stylesheet" href="/res/css/_basic.css" type="text/css">
<link rel="stylesheet" href="/res/css/article.css" type="text/css">
<link rel="stylesheet" href="/res/css/forum.css" type="text/css">
<link rel="stylesheet" href="/res/css/ban.css" type="text/css">
<link rel="stylesheet" href="/res/css/poll.css" type="text/css">
<link rel="stylesheet" href="/res/css/competition.css" type="text/css">
<link rel="stylesheet" href="/res/css/userInfo.css" type="text/css">
<link rel="stylesheet" href="/res/zebra_datepicker.css" type="text/css">
<style type="text/css">
    .col-left {
        width: 210px;
    }
    .col-left .box .in {
        width: 200px;
    }
    .col-center {
        width: 530px;
    }
    .col-center .box .in {
        width: 520px;
    }
    .col-right {
        width: 210px;
    }
    .col-right .box .in {
        width: 200px;
    }
</style>
<script type="text/javascript" src="/res/jquery-3.2.1.min.js"></script>
<script type="text/javascript" src="/res/linkify-2.1.4.min.js"></script>
<script type="text/javascript" src="/res/linkify-jquery-2.1.4.min.js"></script>
<script type="text/javascript" src="/res/jquery.highlight.js"></script>
<script type="text/javascript" src="/res/zebra_datepicker.js"></script>
<script type='text/javascript'>
$(document).ready(function()
{
    $("input.datepicker").Zebra_DatePicker();
    $(".text").each(function() {
        $(this).html($(this).html().replace(/::biggrin::/g, '<img class="smile" src="/res/img/smiles/biggrin.gif"/>'));
        $(this).html($(this).html().replace(/::confused::/g, '<img class="smile" src="/res/img/smiles/confused.gif"/>'));
        $(this).html($(this).html().replace(/::cool::/g, '<img class="smile" src="/res/img/smiles/cool.gif"/>'));
        $(this).html($(this).html().replace(/::cry::/g, '<img class="smile" src="/res/img/smiles/cry.gif"/>'));
        $(this).html($(this).html().replace(/::eek::/g, '<img class="smile" src="/res/img/smiles/eek.gif"/>'));
        $(this).html($(this).html().replace(/::evil::/g, '<img class="smile" src="/res/img/smiles/evil.gif"/>'));
        $(this).html($(this).html().replace(/::frown::/g, '<img class="smile" src="/res/img/smiles/frown.gif"/>'));
        $(this).html($(this).html().replace(/::lol::/g, '<img class="smile" src="/res/img/smiles/lol.gif"/>'));
        $(this).html($(this).html().replace(/::mad::/g, '<img class="smile" src="/res/img/smiles/mad.gif"/>'));
        $(this).html($(this).html().replace(/::neutral::/g, '<img class="smile" src="/res/img/smiles/neutral.gif"/>'));
        $(this).html($(this).html().replace(/::razz::/g, '<img class="smile" src="/res/img/smiles/razz.gif"/>'));
        $(this).html($(this).html().replace(/::redface::/g, '<img class="smile" src="/res/img/smiles/redface.gif"/>'));
        $(this).html($(this).html().replace(/::rolleyes::/g, '<img class="smile" src="/res/img/smiles/rolleyes.gif"/>'));
        $(this).html($(this).html().replace(/::smile::/g, '<img class="smile" src="/res/img/smiles/smile.gif"/>'));
        $(this).html($(this).html().replace(/::wink::/g, '<img class="smile" src="/res/img/smiles/wink.gif"/>'));
        $(this).html($(this).html().replace(/::talking::/g, '<img class="smile" src="/res/img/smiles/talking.gif"/>'));
        $(this).html($(this).html().replace(/::spew::/g, '<img class="smile" src="/res/img/smiles/spew.gif"/>'));
        $(this).html($(this).html().replace(/::facepalm::/g, '<img class="smile" src="/res/img/smiles/facepalm.gif"/>'));
        $(this).html($(this).html().replace(/::thumbsup::/g, '<img class="smile" src="/res/img/smiles/thumbsup.gif"/>'));
        $(this).html($(this).html().replace(/::thumbsdown::/g, '<img class="smile" src="/res/img/smiles/thumbsdown.gif"/>'));
        $(this).html($(this).html().replace(/\\n/g, '<br/>'));
    });
    $(".text").linkify({
        target: "_blank"
    });
    $(".text").highlight($("#searchTextField").val());
    $(".highlight").css({ backgroundColor: "#FFFF88" });
});
</script>
</head>
<body>""" % self.localizer.getDictionary()

    def get_footer(self):
        return """<div class="footer">
<div class="l"><div class="fl">
%(footer-created-label)s %(footer-author)s, %(footer-year)s
</div></div>
<div class="r">
%(footer-version-label)s <a href="%(footer-public-repo)s" class="link">%(version-hash)s</a>
</div>
<div class="cl"></div>
</div>
</div>
</div>
</div>
</body>
</html>""" % self.localizer.getDictionary()

    def get_pages_count(self, posts_count):
        if posts_count > 0:
            pages_count = int(posts_count / POSTS_PER_PAGE)
            if (posts_count % POSTS_PER_PAGE) > 0:
                pages_count += 1
        else:
            pages_count = 1
        return pages_count

    def get_pagination(self):
        html = """<div class="box green"><div class="in c"><div class="pageslist"><table cellspacing="0" cellpadding="0"><tbody><tr><td>
<a href="/?a=%(author-quoted)s&s=%(search-quoted)s&p=1&f=%(search_from)s&t=%(search_to)s&o=%(order)s"><span class="pg-bb">&nbsp;</span></a><div class="dl"></div>""" % self.localizer.getDictionary()

        if (self.page - 7) < 1:
            floor = 1
        else:
            floor = self.page - 7

        if (self.page + 7) > self.pages_count:
            top = self.pages_count
        else:
            top = self.page + 7

        for i in range(self.page - floor):
            html += """<a href="/?a=%s&s=%s&p=%d&f=%s&t=%s&o=%s">%d</a><div class="dl"></div>""" % (quote(self.author), quote(self.search), i + floor, self.search_from, self.search_to, self.order, i + floor)

        html += """<div class="actual">%d</div><div class="dl"></div>""" % (self.page)

        for i in range(top - self.page):
            html += """<a href="/?a=%s&s=%s&p=%d&f=%s&t=%s&o=%s">%d</a><div class="dl"></div>""" % (quote(self.author), quote(self.search), i + self.page + 1, self.search_from, self.search_to, self.order, i + self.page + 1)

        html += """<a href="/?a=%(author-quoted)s&s=%(search-quoted)s&p=%(pages_count)d&f=%(search_from)s&t=%(search_to)s&o=%(order)s"><span class="pg-ff">&nbsp;</span></a><div class="cl"></div>
</td></tr></tbody></table></div></div></div>""" % self.localizer.getDictionary()
        return html

    def get_search(self):
        return """<div class="box"><div class="in">
<form action="/" method="get" class="search">
<input placeholder="%(search-author)s" type="text" name="a" class="field" id="searchUserField" value="%(author)s">
<input placeholder="%(search-text)s" type="text" name="s" class="field" id="searchTextField" value="%(search)s">
<input placeholder="%(search-from)s" type="text" name="f" class="field datepicker" id="fromDateField" value="%(search_from)s">
<input placeholder="%(search-to)s" type="text" name="t" class="field datepicker" id="toDateField" value="%(search_to)s">
<input type="hidden" name="o" value="%(order)s">
<input type="submit" value="" class="submit">
</form>
<div class="cl"></div></div></div>""" % self.localizer.getDictionary()

    def get_pre_forum(self):
        html = """<div class="screen">
<div class="all">
<div class="main">
<div class="header">
  <a href="/" title="" class="home-link"><span>%(web-name)s</span></a>
  <span class="info">%(web-subname)s</span>
</div>
<div class="cl h10"></div>
<div class="middle">
<div class="col-left">""" % self.localizer.getDictionary()
        html += self.get_ranking()
        html += """</div>
<div class="col-center">
<div class="article">
</div>"""
        html += self.get_search()
        html += self.get_pagination()
        html += """<div class="box green">
  <div class="in">
    <div class="bookmark">
      <span class="it active">%(page-counter-label)s %(page)d/%(pages_count)d</span>
      <span class="it %(active-funniest)s" style="float: right">%(funniest-tab)s</span>
      <span class="dl" style="float: right"></span>
      <span class="it %(active-newest)s" style="float: right">%(newest-tab)s</span>
      <div class="border"></div>
    </div>
    <div class="forum">""" % self.localizer.getDictionary()
        return html

    def get_post_forum(self):
        html = """</div>
  </div>
</div>"""
        html += self.get_pagination()
        html += """</div><div class="col-right">"""
        html += self.get_donation_ranking()
        html += """</div></div>"""
        return html

    def create_post(self, post):
        author = post["account_name"]
        html = """<div class="post"><div><a href="?a=%s&s=%s&f=%s&t=%s&o=%s" class="fl name user-link">""" % (quote(author), quote(self.search), self.search_from, self.search_to, self.order)
        html += author
        html += """</a>"""

        try:
            alias = self.localizer.getAliases()[author]
        except KeyError:
            alias = ""
        if alias:
            html += """<div class="fl" style="color: #656565; padding-right: 5px">(%s)</div>""" % alias

        html += """<div class="fl time">"""
        html += post["created"].strftime("%d.%m.%Y %H:%M")
        html += """</div><div class="cl"></div></div><div class="text">"""
        content = post["body"]
        html += content
        html += """</div><div class="links"><div class="fl"><a href=\""""
        if post["page_category"] == 'article':
            link = "https://www.eurofotbal.cz/clanky/-%s/?forum=1#post%s" % (str(post["page_id"]), str(post["anchor"]))
        else:
            link = "https://www.eurofotbal.cz/serie-a/reportaz/-%s/?forum=1#post%s" % (str(post["page_id"]), str(post["anchor"]))
        html += link
        html += """\" class="forumreply" target="_blank">[%s]</a></div><div class="cl"></div></div></div>""" % post["page_name"]
        return html

    def get_ranking(self):
        html = """<div class="box green"><div class="in"><div class="bookmark"><span class="it active">%(top-users)s</span>
<span class="dl"></span><div class="border"></div></div>
<div>""" % self.localizer.getDictionary()

        if not self.search_to:
            t = datetime.today()
        else:
            t = datetime.strptime(self.search_to, "%Y-%m-%d")
        t = t.replace(hour=23, minute=59)

        users = []
        if self.search_from:
            f = datetime.strptime(self.search_from, "%Y-%m-%d")
            f = f.replace(hour=0, minute=0)
            td = t - f
            if not td.days > 365:
                users = Account.select(Account.name, fn.Count(Post.id).alias("count")).join(Post).where(Post.created >= f).where(Post.created <= t).group_by(Account.name).order_by(SQL("count desc")).limit(USER_LIST)
        else:
            users = Postcache.select().order_by(Postcache.count.desc()).offset(1).limit(USER_LIST)

        if users:
            html += """<table cellspacing="0" cellpadding="0"><tbody>
<tr><th>%(user-label)s</th><th>%(comments-label)s</th></tr>""" % self.localizer.getDictionary()
            for user in users:
                try:
                    alias = self.localizer.getAliases()[user.name]
                    alias = """<div class="fl" style="color: #656565; padding-left: 5px">(%s)</div>""" % alias
                except KeyError:
                    alias = ""

                html += """<tr><td><div class="fl"><a href="?a=%s&s=%s&f=%s&t=%s&o=%s">%s</a></div>%s</td><td>%d</td></tr>""" % (quote(user.name), quote(self.search), self.search_from, self.search_to, self.order, user.name, alias, user.count)
            html += """</tbody></table>"""
        else:
            html += """<div style="text-align: center"><b>%(big-interval)s</b></div>""" % self.localizer.getDictionary()

        html += """</div></div></div>"""
        return html

    def get_donation_ranking(self):
        html = """<div class="box green"><div class="in"><div class="bookmark"><span class="it active">%(top-donators)s</span>
        <span class="dl"></span><div class="border"></div></div>
        <div><table cellspacing="0" cellpadding="0">
        <tbody>
        <tr><th>%(user-label)s</th><th>%(how-much)s</th></tr>""" % self.localizer.getDictionary()

        donations = self.localizer.getDonations()
        for record in donations:
            try:
                alias = self.localizer.getAliases()[record[0]]
                alias = """<div class="fl" style="color: #656565; padding-left: 5px">(%s)</div>""" % alias
            except KeyError:
                alias = ""

            if record[0].startswith('?'):
                html += """<tr><td><div class="fl">%s</div></td><td>%s</td></tr>""" % (record[0][1:], record[1])
            else:
                html += """<tr><td><div class="fl"><a href="?a=%s">%s</a></div>%s</td><td>%s</td></tr>""" % (quote(record[0]), record[0], alias, record[1])

        html += """</tbody></table></div></div></div>"""

        html += """<div class="cl h10"></div>
            <div style="text-align: center;"><a href="https://www.buymeacoffee.com/efsearch" target="_blank">Přispějte</a> na tento projekt.</div>
            <div class="cl h10"></div>
            <div style="text-align: center;">Děkuji! ❤️</div>"""

        return html

    def get_forum(self):
        count = 0
        forum = ""

        if self.page <= 0:
            return count, forum

        posts = (Post.select(Account.name.alias("account_name"),
                             Post.created,
                             Post.body,
                             Post.anchor,
                             Page.name.alias("page_name"),
                             Page.ef_id.alias("page_id"),
                             Pagecategory.name.alias("page_category"), )
                    .join(Account, on=(Account.id == Post.account_id))
                    .join(Page, on=(Page.id == Post.page_id))
                    .join(Pagecategory, on=(Pagecategory.id == Page.page_category_id))
                    .dicts())
        if self.author:
            try:
                Account.get(Account.name == self.author)
            except Account.DoesNotExist:
                forum += """<div style="text-align: center"><b>%(unknown-user)s</b><br/><img src="/res/img/wrong.png"></div>""" % self.localizer.getDictionary()
                return count, forum
            posts = posts.where(Account.name == self.author)

        if self.search:
            posts = posts.where(Post.body.contains(self.search))

        if self.search_from:
            f = datetime.strptime(self.search_from, "%Y-%m-%d")
            f = f.replace(hour=0, minute=0)
            posts = posts.where(Post.created >= f)

        if self.search_to:
            t = datetime.strptime(self.search_to, "%Y-%m-%d")
            t = t.replace(hour=23, minute=59)
            posts = posts.where(Post.created <= t)

        # For better performance, there aren't smaller tokens in index?
        if self.search and len(self.search) < 3:
            forum += """<div style="text-align: center"><b>%(short-search)s</b><br/><img src="/res/img/wrong.png"></div>""" % self.localizer.getDictionary()
            return count, forum

        if self.search or self.search_from or self.search_to:
            count = posts.count()
        else:
            count = Postcache.get(Postcache.name == self.author).count

        if count <= 0:
            forum += """<div style="text-align: center"><b>%(not-found)s</b><br/><img src="/res/img/wrong.png"></div>""" % self.localizer.getDictionary()
            return count, forum

        if self.order == 'f':
            posts = posts.order_by(Post.funny_ranking.desc())
        elif self.order == 'n':
            posts = posts.order_by(Post.created.desc())

        for post in posts.paginate(self.page, POSTS_PER_PAGE):
            forum += self.create_post(post)

        return count, forum

    def get_content(self):
        (posts_count, forum) = self.get_forum()
        self.pages_count = self.get_pages_count(posts_count)
        self.localizer.set("pages_count", self.pages_count)

        return self.get_pre_forum() + forum + self.get_post_forum()

