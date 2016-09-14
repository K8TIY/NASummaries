#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys
import re,getopt,codecs,cgi,time,shutil
try:
  from HTMLParser import HTMLParser
except ImportError:
  from html.parser import HTMLParser
hp = HTMLParser()


def latexHeader(f,dotitle):
  title = "No Agenda Summaries"
  f.write(r"""\documentclass{report}
\usepackage{fontspec}
\usepackage{fancyvrb}
\usepackage{enumitem}
\usepackage[normalem]{ulem}
\usepackage{censor}
\usepackage[colorlinks=true]{hyperref}
\setlist{nolistsep}
\setlist{noitemsep}
\newcommand{\mono}[1]{{\fontspec{Courier}#1}}
\newcommand{\scmono}[1]{{\fontspec{Source Code Pro}#1}}
\newcommand{\cjk}[1]{{\fontspec[Scale=0.9]{Hiragino Mincho Pro}#1}}
\newcommand{\asymbol}[1]{{\fontspec[Scale=0.9]{Apple Symbols}#1}}
\addtolength{\oddsidemargin}{-.6in}
\addtolength{\evensidemargin}{-.6in}
\addtolength{\textwidth}{1.2in}
\setlength{\parindent}{0pt}
\usepackage{titlesec}
%\titleformat{\section}[display]{\large}{\thetitle}{1em}{#1\space\xrfill[0.6ex]{0.4pt}}
\renewcommand*\thesection{\arabic{section}}
\newcommand{\doulos}[1]{{\fontspec{Doulos SIL}#1}}

\begin{document}
\title{{\Huge \mono{""" + title + r"""}}}
\author{Sir Ludark Babark Fudgefountain, \scmono{K8TIY}}
\date{\parbox{\linewidth}{\centering%
  \today\endgraf\bigskip
  \textit{This document and all associated media and software\\are hereby placed in
  the public domain.}}}
""")
  if dotitle:
    f.write('\maketitle\n')

def latexSection(f,lines,shownum,showdate):
  shownum = re.sub(r'^(\d+\.?\d*).*$', r'\1', lines[0])
  f.write("\\renewcommand{\\thesection}{%s}\n" % (shownum))
  f.write("\\section[%s]{%s \\small{(%s)}}\n" % (latexEscape(lines[2]),latexEscape(lines[2]),showdate))
  f.write("\\begin{itemize}\n")
  for i in xrange(3,len(lines)):
    if len(lines[i]) > 0:
      parts = lines[i].split(None, 1)
      label = "\\scmono{%s}" % (parts[0])
      if float(shownum) >= 559:
        urltime = re.sub(':', '-', parts[0])
        label = "\\href{https://www.noagendaplayer.com/listen/%s/%s}{%s}" % (shownum, urltime, label)
      f.write("\\item[%s]%s\n" % (label, latexEscape(parts[1])))
  f.write("\\end{itemize}\\newpage\n")

# Educate quotes and format stuff
def latexEscape(s):
  s = re.sub(r'\s\s+', r'\\\\', s)
  s = re.sub(r'&', r'\&', s)
  s = re.sub(r'#', r'\#', s)
  s = re.sub(r'%', r'\%', s)
  s = re.sub(r'\$', r'\$', s)
  s = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', s)
  s = re.sub(r'\*(.+?)\*', r'\\textit{\1}', s)
  s = re.sub(r'~~~(.+?)~~~', r'\\censor{abcdefg}', s)
  s = re.sub(r'~~(.+?)~~', r'\\sout{\1}', s)
  s = re.sub(r'(\d:\d\d:\d\d)', r'\\scmono{\1}', s)
  s = re.sub(r'``(.+?)``', r'\\scmono{\1}', s)
  s = re.sub(r'`(.+?)`', r'\\texttt{\1}', s)
  s = re.sub(r'\[\[(\[*.+?\]*)\]\]', r'\\doulos{\1}', s)
  s = re.sub(r'\[\]', r'\\ ', s)
  s = re.sub(r'{{(.+?)}}', r'$\mathrm{\1}$', s)
  s = re.sub(u'([\u0400-\u052F]+)', r'\\doulos{\1}', s)
  s = re.sub(u'([\u0370-\u03FF]+)', r'\\doulos{\1}', s)
  s = re.sub(u'([\u16A0-\u16FF]+)', r'\\asymbol{\1}', s)
  s = re.sub(r'__(.+?)__', r'\\cjk{\1}', s)
  s = re.sub(r'\\&ast;', '*', s)
  s = re.sub(r'\(CotD\)', '({\\color{red}CotD})', s)
  s = hp.unescape(s)
  news = ''
  oq = False
  for i in xrange(0,len(s)):
    c = s[i]
    if c == '"':
      if not oq:
        c = '``'
        oq = True
      else: oq = False
    news = news + c
  s = news
  s = re.sub(r'\\(\'+)', r'$\1$', s)
  return s


def HTMLPage(f,lines,shownum,showdate):
  HTMLHeader(f,'No Agenda %s' % (lines[0]),shownum)
  f.write('<h3>%s <i>%s</i> <span style="font-size:.6em;">(%s)</span></h3>' % (shownum,lines[2],showdate))
  f.write("<table>")
  for i in xrange(3,len(lines)):
    if len(lines[i]) > 0 and lines[i] != '~~~~':
      parts = lines[i].split(None, 1)
      s = re.sub(r'(\d:\d\d:\d\d)', r'<code>\1</code>', cgi.escape(parts[1]))
      s = re.sub(r'\s\s+', r'<br/>', s)
      s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
      s = re.sub(r'\*(.+?)\*', r'<i>\1</i>', s)
      s = re.sub(r'&amp;ast;', '*', s)
      s = re.sub(r'~~~(.+?)~~~', r'<span style="background:black">&nbsp;&nbsp;&nbsp;&nbsp;</span>', s)
      s = re.sub(r'~~(.+?)~~', r'<s>\1</s>', s)
      s = re.sub(r'(\d:\d\d:\d\d)', r'<code>\1</code>', s)
      s = re.sub(r'``(.+?)``', r'<code>\1</code>', s)
      s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
      s = re.sub(r'`', r'&lsquo;', s)
      s = re.sub(r"'", r'&rsquo;', s)
      s = re.sub(r'\[\]', r' ', s)
      s = re.sub(r'\[\[(\[*.+?\]*)\]\]', r'\1', s)
      s = re.sub(r'{{(.+?)}}', r'\1', s)
      s = re.sub(r'_(\S*)', r'<sub>\1</sub>', s)
      s = re.sub(r'\\{', r'{', s)
      s = re.sub(r'\\}', r'}', s)
      s = re.sub(r'\\(\'+)', r'\1', s)
      s = re.sub(r'__(.+?)__', r'\1', s)
      label = "<code>%s</code>" % (parts[0])
      news = ''
      oq = False
      for i in xrange(0,len(s)):
        c = s[i]
        if c == '"':
          if not oq:
            c = '&ldquo;'
            oq = True
          else:
            c = '&rdquo;'
            oq = False
        news = news + c
      s = news
      s = re.sub(r'\(CotD\)', '(<span style="color:red;">CotD</span>)', s)
      if float(shownum) >= 559:
        urltime = re.sub(':', '-', parts[0])
        label = "<a href='https://www.noagendaplayer.com/listen/%s/%s' target='_blank'>%s</a>" % (shownum, urltime, parts[0])
      f.write("<tr><td style='padding-right:5px;vertical-align:top;'><code>%s</code></td><td>%s</td></tr>\n" % (label,s))
  f.write("</table></div></div></div></body></html>\n")


def HTMLHeader(f,title,shownum=None):
  google = """<div>
  <script type="text/javascript">
    (function() {
      var cx = '000307461187542395848:qdygkg6ssbo';
      var gcse = document.createElement('script');
      gcse.type = 'text/javascript';
      gcse.async = true;
      gcse.src = (document.location.protocol == 'https:' ? 'https:' : 'http:') +
          '//www.google.com/cse/cse.js?cx=' + cx;
      var s = document.getElementsByTagName('script')[0];
      s.parentNode.insertBefore(gcse, s);
    })();
  </script>
  <div class="gcse-search"></div>
</div>"""
  if shownum is not None:
    google = ''
  snLink = ''
  homeLink = ''
  if shownum is not None:
    homeLink = '<li><a href="index.html">Home</a></li>'
    snLink = '<li><a href="http://%s.nashownotes.com" target="_blank">Show Notes</a></li>' % shownum
  f.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
  <link rel="stylesheet" type="text/css" media="all" href="na.css"/>
  <title>%s</title>
</head>
<body>
%s
<div class="container">
  <div class="header">
    <h1 class="header-heading">Call Clooney!</h1>
  </div>
  <div class="nav-bar">
    <ul class="nav">
      %s
      %s
      <li><a href="http://noagendashow.com">No Agenda Show</a></li>
      <li><a href='https://github.com/K8TIY/NASummaries'>Github</a></li>
      <li><a href="NASummaries.pdf"><img alt="PDF" src="pdf-icon.png" width="20" height="20"/>   Full PDF</a></li>
    </ul>
  </div>
  <div class="content">
    <div class="main">
""" % (title,google,homeLink,snLink))


if __name__ == '__main__':
  def usage():
    print """Usage: NASummaries.py [OPTIONS]
  Read NASummaries.txt, produce derivative HTML and/or LaTeX files,
  and optionally upload them to a webserver.

    -d, --delete     Delete the LaTeX file after rendering PDF
    -g, --git        Commit and push to repo
    -h, --help       Print this summary and exit
    -H, --HTML       Create HTML
    -i, --input      Read from argument instead of NASummaries.txt
    -l, --latex      Create LaTeX
    -n, --number     Use this number as the Show number in the git commit
    -N, --noop       Do not execute rsync or git that would touch a remote site
    -t, --title      Suppress the title page
    -u, --upload     rsync to callclooney.org
  """
  delLtx = False
  git = False
  latex = False
  latexout = None
  htmlout = None
  ind = None
  sitemap = None
  html = False
  shownum = None
  noop = False
  title = True
  upload = False
  infile = None
  shortopts = "dghHi:n:Nltu"
  longopts = ["delete","git","help","HTML","input=","latex","number=","noop",
              "title","upload"]
  try:
    [opts,args] = getopt.getopt(sys.argv[1:],shortopts,longopts)
  except getopt.GetoptError,why:
    print("could not understand command line options: %s" % why)
    usage()
    sys.exit(-1)
  for [o,a] in opts:
    if o == '-d' or o == '--delete': delLtx = True
    if o == '-g' or o == '--git': git = True
    elif o == '-h' or o == '--help':
      usage()
      sys.exit(0)
    elif o == "-H" or o == "--HTML": html = True
    elif o == "-i" or o == "--input": infile = a
    elif o == "-l" or o == "--latex": latex = True
    elif o == "-n" or o == "--number": shownum = a
    elif o == "-N" or o == "--noop": noop = True
    elif o == "-t" or o == "--title": title = False
    elif o == "-u" or o == "--upload": upload = True
  if latex:
    latexout = codecs.open("NASummaries.tex", "w", "utf-8")
    latexHeader(latexout, title)
  maxshow = 0
  if infile is None: infile = 'NASummaries.txt'
  with codecs.open(infile, 'r', "utf-8") as x: f = x.read()
  try: os.mkdir("na");
  except Exception as e: pass
  summs = re.split("\n\n+", f)
  summs.reverse()
  now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time()))
  if html:
    shutil.copy2('na.css', 'na/na.css')
    shutil.copy2('pdf-icon.png', 'na/pdf-icon.png')
    ind = codecs.open("na/index.html", "w", "utf-8")
    HTMLHeader(ind,"No Agenda Show Summaries")
    ind.write('''<h1>No Agenda Show Summaries
  <a rel="license" href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/p/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
</h1>
<h4>Shut up, slave!</h4><hr/>''')
    sitemap = codecs.open("na/sitemap.xml", "w", "utf-8")
    sitemap.write('''<?xml version="1.0" encoding="UTF-8"?>
<urlset
      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
            http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
  <url>
    <loc>http://www.blugs.com/na/index.html</loc>
    <lastmod>%s</lastmod>
    <changefreq>daily</changefreq>
  </url>
  <url>
    <loc>http://www.blugs.com/na/NASummaries.pdf</loc>
    <lastmod>%s</lastmod>
    <changefreq>daily</changefreq>
  </url>''' % (now,now))
  for summ in summs:
    if len(summ) == 0: continue
    lines = summ.split("\n")
    n = re.sub(r'^(\d+\.?\d*).*$', r'\1', lines[0])
    showdate = lines[1]
    showdate = re.sub(r'(\d+)/(\d+)/(\d+)', r'\3-\1-\2', showdate)
    if n > maxshow: maxshow = n
    if latex: latexSection(latexout,lines,n,showdate)
    if html:
      htmlname = "%s_NASummary.html" % (n)
      url = "http://www.blugs.com/na/" + htmlname
      htmlout = codecs.open('na/' + htmlname, "w", "utf-8")
      HTMLPage(htmlout,lines,n,showdate)
      ind.write("<a href='%s'><strong>%s</strong> (%s) <i>%s</i></a><br/>\n" %
                (htmlname, lines[0], showdate, cgi.escape(lines[2])))
      htmlout.close()
      sitemap.write('''  <url>
    <loc>%s</loc>
    <lastmod>%s</lastmod>
    <changefreq>daily</changefreq>
  </url>\n''' % (url,now))
  if latexout is not None:
    latexout.write("\end{document}\n")
    latexout.close()
    res = os.system('xelatex -output-directory=na NASummaries.tex')
    try:
      os.unlink('na/NASummaries.aux')
      os.unlink('na/NASummaries.log')
      os.unlink('na/NASummaries.out')
      if delLtx and res==0: os.unlink('NASummaries.tex')
    except Exception as e: pass
  if ind is not None:
    ind.write("</div></div></div></body></html>\n")
    ind.close()
  if sitemap is not None:
    sitemap.write('''  <url>
    <loc>"http://www.blugs.com/na/NASummaries.pdf"</loc>
    <lastmod>%s</lastmod>
    <changefreq>daily</changefreq>
  </url>\n</urlset>\n''' % (now))
    sitemap.close()
  if upload is True:
    cmd = "rsync -azrlv --exclude='.DS_Store' -e ssh na/ blugs@blugs.com:blugs.com/na"
    if noop:
      print "noop set; not executing '%s'" % (cmd)
    else:
      os.system(cmd)
  if git is True:
    if shownum is not None: maxshow = shownum
    cmd = "git commit -m 'Show %s.' NASummaries.txt" % (maxshow)
    cmd2 = "git push origin master"
    if noop:
      print "noop set; not executing '%s' for %s, %s" % (cmd, shownum, maxshow)
    else:
      os.system(cmd)
      os.system(cmd2)
