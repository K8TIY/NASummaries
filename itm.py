#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys
import re,getopt,codecs,cgi,time

def latexHeader(f,dotitle):
  title = "No Agenda Summaries"
  f.write(r"""\documentclass{report}
\usepackage{fontspec}
\usepackage{fancyvrb}
\usepackage{enumitem}
\usepackage[normalem]{ulem}
\usepackage{censor}
\setlist{nolistsep}
\setlist{noitemsep}
\newcommand{\mono}[1]{{\fontspec{Courier}#1}}
\newcommand{\scmono}[1]{{\fontspec{Source Code Pro}#1}}
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
""")
  if dotitle:
    f.write('\maketitle\n')

def latexSection(f,lines):
  shownum = re.sub(r'^(\d+\.?\d*).*$', r'\1', lines[0])
  f.write("\\renewcommand{\\thesection}{%s}\n" % (shownum))
  f.write("\\section[%s]{%s \\small{(%s)}}\n" % (latexEscape(lines[2]),latexEscape(lines[2]),lines[1]))
  f.write("\\begin{itemize}\n")
  for i in xrange(3,len(lines)):
    if len(lines[i]) > 0:
      if lines[i] == '~~~~':
        f.write("\\newpage \n")
      else:
        parts = lines[i].split(None, 1)
        f.write("\\item[\\mono{%s}]%s\n" % (parts[0],latexEscape(parts[1])))
  f.write("\\end{itemize}\n")

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
  s = re.sub(r'(\d:\d\d:\d\d)', r'\\texttt{\1}', s)
  s = re.sub(r'``(.+?)``', r'\\scmono{\1}', s)
  s = re.sub(r'`(.+?)`', r'\\texttt{\1}', s)
  s = re.sub(r'\[\[(\[*.+?\]*)\]\]', r'\\doulos{\1}', s)
  s = re.sub(r'\[\]', r'\\ ', s)
  s = re.sub(r'{{(.+?)}}', r'$\mathrm{\1}$', s)
  s = re.sub(u'([\u0400-\u052F]+)', r'\\doulos{\1}', s)
  s = re.sub(u'([\u0370-\u03FF]+)', r'\\doulos{\1}', s)
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


def HTMLPage(f,lines):
  HTMLHeader(f,cgi.escape('%s %s "%s"' % (lines[0],lines[1],lines[2])))
  f.write('<h3>%s %s "%s"</h3>' % (lines[0],lines[1],lines[2]))
  f.write('<h5><a href="http://%s.nashownotes.com" target="_blank">Show Notes</a></h5>' % (lines[0]))
  f.write("<table>")
  for i in xrange(3,len(lines)):
    if len(lines[i]) > 0 and lines[i] != '~~~~':
      parts = lines[i].split(None, 1)
      s = re.sub(r'(\d:\d\d:\d\d)', r'<code>\1</code>', cgi.escape(parts[1]))
      s = re.sub(r'\s\s+', r'<br/>', s)
      s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
      s = re.sub(r'\*(.+?)\*', r'<i>\1</i>', s)
      s = re.sub(r'~~~(.+?)~~~', r'<span style="background:black">&nbsp;&nbsp;&nbsp;&nbsp;</span>', s)
      s = re.sub(r'~~(.+?)~~', r'<s>\1</s>', s)
      s = re.sub(r'(\d:\d\d:\d\d)', r'<code>\1</code>', s)
      s = re.sub(r'``(.+?)``', r'<code>\1</code>', s)
      s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
      s = re.sub(r'\[\]', r' ', s)
      s = re.sub(r'\[\[(\[*.+?\]*)\]\]', r'\1', s)
      s = re.sub(r'{{(.+?)}}', r'\1', s)
      s = re.sub(r'_(\S*)', r'<sub>\1</sub>', s)
      s = re.sub(r'\\{', r'{', s)
      s = re.sub(r'\\}', r'}', s)
      s = re.sub(r'\\(\'+)', r'\1', s)
      f.write("<tr><td style='padding-right:5px;vertical-align:top;'><code>%s</code><td>%s</td></tr>\n" % (parts[0],s))
  f.write("</table></body></html>\n")


def HTMLHeader(f,title):
  f.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
  <title>%s</title>
</head>
<body>
<div>
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
</div>
""" % (title))


if __name__ == '__main__':
  def usage():
    print """Usage: NASummaries.py [OPTIONS]
  Read NASummaries.txt, produce derivative HTML and/or LaTeX files,
  and optionally upload them to a webserver.

    -d, --delete     Delete the LaTeX file after rendering PDF.
    -h, --help       Print this summary and exit.
    -H, --HTML       Create HTML.
    -i, --input      Read from argument instead of NASummaries.txt
    -l, --latex      Create LaTeX.
    -t, --title      Suppress the title page
    -u, --upload     rsync to callclooney.org
  """
  delLtx = False
  latex = False
  latexout = None
  htmlout = None
  ind = None
  sitemap = None
  html = False
  title = True
  upload = False
  infile = None
  shortopts = "dhHi:ltu"
  longopts = ["delete","help","HTML","input=","latex","title","upload"]
  try:
    [opts,args] = getopt.getopt(sys.argv[1:],shortopts,longopts)
  except getopt.GetoptError,why:
    print("could not understand command line options: %s" % why)
    usage()
    sys.exit(-1)
  for [o,a] in opts:
    if o == '-d' or o == '--delete': delLtx = True
    elif o == '-h' or o == '--help':
      usage()
      sys.exit(0)
    elif o == "-H" or o == "--HTML": html = True
    elif o == "-i" or o == "--input": infile = a
    elif o == "-l" or o == "--latex": latex = True
    elif o == "-t" or o == "--title": title = False
    elif o == "-u" or o == "--upload": upload = True
  if latex:
    latexout = codecs.open("NASummaries.tex", "w", "utf-8")
    latexHeader(latexout, title)
  
  if infile is None: infile = 'NASummaries.txt'
  with codecs.open(infile, 'r', "utf-8") as x: f = x.read()
  summs = re.split("\n\n+", f)
  summs.reverse()
  now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time()))
  if html:
    try: os.mkdir("na");
    except Exception as e: pass
    ind = codecs.open("na/index.html", "w", "utf-8")
    HTMLHeader(ind,"No Agenda summaries")
    ind.write("<h3><a href='http://noagendashow.com'>No Agenda</a> summaries</h3>")
    ind.write("<p>PDF of all show summaries <a href='NASummaries.pdf'>here</a></p>")
    ind.write("""<p>Original source files and tools, plus notes on philosophy
              and schedule, are on
              <a href='https://github.com/K8TIY/NASummaries'>GitHub</a></p>""")
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
    if latex: latexSection(latexout,lines)
    if html:
      shownum = re.sub(r'^(\d+\.?\d*).*$', r'\1', lines[0])
      htmlname = "%s_NASummary.html" % (shownum)
      url = "http://www.blugs.com/na/" + htmlname
      htmlout = codecs.open('na/' + htmlname, "w", "utf-8")
      HTMLPage(htmlout,lines)
      ind.write("<a href='%s'>%s %s \"%s\"</a><br/>\n" %
                (htmlname, lines[0], lines[1], lines[2]))
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
      if delLtx and res==0: os.unlink('NASummaries.tex')
    except Exception as e: pass
  if ind is not None:
    ind.write("</body></html>\n")
    ind.close()
  if sitemap is not None:
    sitemap.write("</urlset>")
    sitemap.close()
  if upload is True:
    os.system("rsync -azrlv --exclude='.DS_Store' -e ssh na/ blugs@blugs.com:blugs.com/na")
