#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys
import re,getopt,codecs,cgi,time,shutil
try:
  # For Python 3.0 and later
  from urllib.request import urlopen
except ImportError:
  # Fall back to Python 2's urllib2
  from urllib2 import urlopen

try:
  xrange
except NameError:
  xrange = range

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'


def latexHeader(f):
  if book: f.write(r"""\documentclass[twoside]{book}
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE,RO]{\thepage}
\fancyhead[LO,RE]{}
\renewcommand{\headrulewidth}{0pt}
""")
  else: f.write(r'\documentclass{report}')
  f.write(r"""\usepackage{tikz}
\usepackage{graphicx}
\usepackage{fontspec}
\usepackage{fancyvrb}
\usepackage{enumitem}
\usepackage[normalem]{ulem}
\usepackage{censor}
\usepackage[colorlinks=true]{hyperref}
\setlist{nolistsep}
\setlist{noitemsep}
\usepackage{dblfloatfix}
\newcommand{\mono}[1]{{\fontspec{Courier}#1}}
\newcommand{\scmono}[1]{{\fontspec{Source Code Pro}#1}}
\newcommand{\cjk}[1]{{\fontspec[Scale=0.9]{Hiragino Mincho Pro}#1}}
\newcommand{\asymbol}[1]{{\fontspec[Scale=0.9]{Apple Symbols}#1}}
\newcommand{\lgrande}[1]{{\fontspec[Scale=0.9]{Lucida Grande}#1}}
\newcommand{\skt}[1]{{\fontspec[Scale=0.9]{Sanskrit 2003}#1}}
\addtolength{\oddsidemargin}{-.6in}
\addtolength{\evensidemargin}{-.6in}
\addtolength{\textwidth}{1.2in}
\setlength{\parindent}{0pt}
\usepackage{titlesec}
%\titleformat{\section}[display]{\large}{\thetitle}{1em}{#1\space\xrfill[0.6ex]{0.4pt}}
\renewcommand*\thesection{\arabic{section}}
\newcommand{\doulos}[1]{{\fontspec{Doulos SIL}#1}}
\begin{document}
""")
  if book and frontmatter:
    f.write(r"""\include{Frontmatter}
\mainmatter""")
  elif frontmatter:
    f.write(r"""\textit{The text of this document and associated software are hereby placed in
the public domain. All image copyrights belong to their respective owners.}
\newpage
""")

def latexSection(f,lines,shownum,showdate,samepage):
  shownum = re.sub(r'^(\d+\.?\d*).*$', r'\1', lines[0])
  f.write("\\renewcommand{\\thesection}{%s}\n" % (shownum))
  pic = "na/art/" + shownum + ".png"
  pic = re.sub(r'\.(\d+\.png)', r'_\1', pic)
  if not os.path.isfile(pic): pic = None
  filler = None
  f.write("\\section[%s]{%s \\small{(%s)}" % (latexEscape(lines[2]),latexEscape(lines[2]),showdate))
  if art == True and pic is not None:
    if lines[3] == 'Artwork':
      filler = pic
    else:
      if not samepage:
        f.write("\\begin{tikzpicture}[remember picture,overlay]"+
                "\\node[xshift=4cm,yshift=-2.3cm] at (current page.north west)"+
                "{\\includegraphics[width=3cm,height=3cm,keepaspectratio]{"+pic+"}};"+
                "\\end{tikzpicture}\n")
      else:
        f.write("\\begin{tikzpicture}[remember picture,overlay]"+
                "\\node[xshift=-4.6cm,yshift=-2.3cm] at (current page.north east)"+
                "{\\includegraphics[width=3cm,height=3cm,keepaspectratio]{"+pic+"}};"+
                "\\end{tikzpicture}\n")
  f.write("}\n")
  f.write("\\begin{itemize}\n")
  nobreak = False
  for i in xrange(3,len(lines)):
    if lines[i] == "Nobreak":
      nobreak = True
    if len(lines[i]) > 0 and lines[i] != "Artwork" and lines[i] != "Nobreak":
      parts = lines[i].split(None, 1)
      label = "\\scmono{%s}" % (parts[0])
      urltime = re.sub(':', '-', parts[0])
      label = "\\href{https://www.noagendaplayer.com/listen/%s/%s}{%s}" % (shownum, urltime, label)
      f.write("\\item[%s]%s\n" % (label, latexEscape(parts[1])))
  f.write("\\end{itemize}\n")
  if filler is not None:
    f.write("\\begin{figure*}[!b]\\begin{center}\\includegraphics[width=.45 \\textwidth,height=.45 \\textheight,keepaspectratio]{"+pic+"}\\end{center}\\end{figure*}")
  if nobreak:
    f.write("\\vspace{.25cm}\n")
  else:
    f.write("\\newpage\n")
  return nobreak

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
  s = re.sub(r'\d+@\d:\d\d:\d\d', lambda m: playerURL(m.group(),'latex'), s)
  s = re.sub(r'(\d:\d\d:\d\d)', r'\\scmono{\1}', s)
  s = re.sub(r'``(.+?)``', r'\\scmono{\1}', s)
  s = re.sub(r'`(.+?)`', r'\\texttt{\1}', s)
  s = re.sub(r'\[\[(\[*.+?\]*)\]\]', r'\\doulos{\1}', s)
  s = re.sub(r'\[\]', r'\\ ', s)
  s = re.sub(r'\[', r'{[}', s)
  s = re.sub(r'\]', r'{]}', s)
  s = re.sub(r'{{(.+?)}}', r'$\mathrm{\1}$', s)
  s = re.sub(u'([\u0400-\u052F]+)', r'\\doulos{\1}', s)
  s = re.sub(u'([\u0370-\u03FF]+)', r'\\lgrande{\1}', s)
  s = re.sub(u'([\u16A0-\u16FF]+)', r'\\asymbol{\1}', s)
  s = re.sub(u'([\u2700-\u27BF]+)', r'\\lgrande{\1}', s)
  s = re.sub(u'([\u20A0-\u20CF]+)', r'\\lgrande{\1}', s)
  s = re.sub(u'([\u0900-\u097F]+)', r'\\skt{\1}', s)
  s = re.sub(r'__(.+?)__', r'\\cjk{\1}', s)
  s = re.sub(r'____', r'\\underline{\\hspace{2em}}', s)
  s = re.sub(r'\\&ast;', '*', s)
  s = re.sub(r'\((B?CotD)\)', r'({\\color{red}\1})', s)
  s = re.sub(r'\(((ACC|JCD)PPotD)\)', r'({\\color{red}\1})', s)
  s = re.sub(r'\(TCS\)', r'({\\color{red}TCS})', s)
  s = re.sub(r'<sub>(.+?)</sub>', r'{\\textsubscript \1}', s)
  s = re.sub(r'<sup>(.+?)</sup>', r'{\\textsuperscript \1}', s)
  s = re.sub(r'<frac>(.+?)/(.+?)</frac>', r'$\\frac{\1}{\2}$', s)
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
  s = re.sub(r'\\&rdquo;', '"', s)
  return s

def playerURL(s,fmt):
  label = s
  parts = re.split(r'\s*@\s*', s, 1)
  shownum = parts[0]
  urltime = re.sub(':', '-', parts[1])
  if fmt == 'latex':
    label = "\\scmono{%s}" % (s)
    label = "\\href{https://www.noagendaplayer.com/listen/%s/%s}{%s}" % (shownum, urltime, label)
  else:
    label = "<code>%s</code>" % (s)
    label = "<a href='https://www.noagendaplayer.com/listen/%s/%s' target='_blank'>%s</a>" % (shownum, urltime, label)
  return label

def HTMLPage(f,lines,shownum,showdate):
  HTMLHeader(f,'No Agenda %s' % (lines[0]),shownum)
  f.write('<h3>%s <b>%s</b> <span style="font-size:.6em;">(%s)</span></h3>' % (shownum,HTMLEscape(lines[2]),showdate))
  pic = "na/art/" + shownum + ".png"
  pic = re.sub(r'\.(\d+\.png)', r'_\1', pic)
  if not os.path.isfile(pic): pic = None
  if pic is not None:
    url = AlbumArtURL(shownum)
    f.write('<div style="text-align:center;">')
    f.write('<img style="max-width:40em;" alt="Show ' + shownum + ' album art" src="' + url + '"/></div>')
  f.write("<table>")
  for i in xrange(3,len(lines)):
    if len(lines[i]) > 0 and lines[i] != "Artwork" and lines[i] != "Nobreak":
      parts = lines[i].split(None, 1)
      label = "<code>%s</code>" % (parts[0])
      s = HTMLEscape(parts[1])
      urltime = re.sub(':', '-', parts[0])
      label = "<a href='https://www.noagendaplayer.com/listen/%s/%s' target='_blank'>%s</a>" % (shownum, urltime, parts[0])
      f.write("<tr><td style='padding-right:5px;vertical-align:top;'><code>%s</code></td><td>%s</td></tr>\n" % (label,s))
  f.write("</table></div></div></div></body></html>\n")

def HTMLEscape(s):
  s = re.sub(r'\\_', '_', s)
  s = re.sub(r'\s\s+', r'<br/>', s)
  s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
  s = re.sub(r'\*(.+?)\*', r'<i>\1</i>', s)
  s = re.sub(r'&amp;ast;', '*', s)
  s = re.sub(r'~~~(.+?)~~~', r'<span style="background:black">&nbsp;&nbsp;&nbsp;&nbsp;</span>', s)
  s = re.sub(r'~~(.+?)~~', r'<s>\1</s>', s)
  s = re.sub(r'``(.+?)``', r'<code>\1</code>', s)
  s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
  s = re.sub(r'`', r'&lsquo;', s)
  s = re.sub(r"'", r'&rsquo;', s)
  s = re.sub(r'\[\]', r' ', s)
  s = re.sub(r'\[\[(\[*.+?\]*)\]\]', r'\1', s)
  s = re.sub(r'{{(.+?)}}', r'\1', s)
  s = re.sub(r'\\{', r'{', s)
  s = re.sub(r'\\}', r'}', s)
  s = re.sub(r'\\(\'+)', r'\1', s)
  s = re.sub(r'__(.+?)__', r'\1', s)
  s = re.sub(r'\d+@\d:\d\d:\d\d', lambda m: playerURL(m.group(),'html'), s)
  s = re.sub(r'\((\d:\d\d:\d\d)\)', r'(<code>\1</code>)', s)
  s = re.sub(r'<frac>(.+?)/(.+?)</frac>', r'<sup>\1</sup>&frasl;<sub>\2</sub>', s)
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
  s = re.sub(r'\((B?CotD)\)', r'(<span style="color:red;">\1</span>)', s)
  s = re.sub(r'\(((ACC|JCD)PPotD)\)', r'(<span style="color:red;">\1</span>)', s)
  s = re.sub(r'\((TCS)\)', r'(<span style="color:red;">\1</span>)', s)
  return s

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
  snLink = ''
  homeLink = ''
  if shownum is not None:
    google = ''
    homeLink = '<li><a href="index.html">Home</a></li>'
    snURL = ShowNotesURL(shownum)
    if snURL is not None:
      snLink = '<li><a href="%s" target="_blank">Show Notes</a></li>' % snURL
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

def ShowNotesURL(shownum):
  if float(shownum) > 581.0: return 'http://%s.noagendanotes.com' % shownum
  elif float(shownum) > 300.0: return 'http://%s.nashownotes.com' % shownum
  return None

def GetAlbumArt(n):
  re.sub
  url = "http://noagendaplayer.com/art/" + n + ".jpg"
  fname = url.split('/')[-1]
  path = "na/art/" + fname
  ppath = re.sub(r'\.jpg$', '.png', path)
  ppath = re.sub(r'\.(\d+\.png)', r'_\1', ppath)
  if not os.path.isfile(ppath):
    if not os.path.isfile(path):
      cmd = "curl -L %s -o %s" % (url, path)
      res = os.system(cmd)
      if res != 0:
        print(bcolors.FAIL + "%s returned %s" % (cmd,res) + bcolors.ENDC)
        sys.exit(1)
    cmd = "sips -s format png -Z 512 %s --out %s" % (path, ppath)
    res = os.system(cmd)
    if res != 0:
      print(bcolors.FAIL + "%s returned %s" % (cmd,res) + bcolors.ENDC)
      sys.exit(1)
    print("%s returned %s" % (cmd,res))
    if os.path.isfile(ppath):
      try: os.unlink(path)
      except Exception as e: pass

def AlbumArtURL(n):
  url = None
  file = 'na/art/' + n + '.png'
  file = re.sub(r'\.(\d+\.png)', r'_\1', file)
  if os.path.isfile(file):
    url = "art/" + n + '.png'
    url = re.sub(r'\.(\d+\.png)', r'_\1', url)
  return url

def RemoveFile(f):
  try: os.unlink(f)
  except Exception as e: pass

if __name__ == '__main__':
  def usage():
    print("""Usage: NASummaries.py [OPTIONS]
  Read NASummaries.txt, produce derivative HTML and/or LaTeX files,
  and optionally upload them to a webserver.

    -a, --art           Include album art in PDF and HTML
    -b, --book          Use LaTeX book class instead of report
    -d, --delete        Delete the LaTeX file after rendering PDF
    -f, --frontmatter   Suppress the frontmatter
    -g, --git           Commit and push to repo
    -h, --help          Print this summary and exit
    -H, --HTML          Create HTML
    -i, --input         Read from argument instead of NASummaries.txt
    -l, --latex         Create LaTeX
    -n, --number        Use this number as the Show number in the git commit
    -N, --noop          Do not execute rsync or git that would touch a remote site
    -t, --title         Suppress the title page
    -u, --upload        rsync to callclooney.org
    -v, --verbose       Print upload and git commands before executing them
  """)
  art = False
  book = False
  delLtx = False
  frontmatter = True
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
  verbose = False
  infile = None
  shortopts = "abdfghHi:n:Nltuv"
  longopts = ["art","book","delete","frontmatter""git","help","HTML","input=","latex",
              "number=","noop","title","upload","verbose"]
  try:
    [opts,args] = getopt.getopt(sys.argv[1:],shortopts,longopts)
  except getopt.GetoptError as why:
    print("could not understand command line options: %s" % why)
    usage()
    sys.exit(-1)
  for [o,a] in opts:
    if o == '-a' or o == '--art': art = True
    if o == '-b' or o == '--book': book = True
    if o == '-d' or o == '--delete': delLtx = True
    if o == '-f' or o == '--frontmatter': frontmatter = False
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
    elif o == "-v" or o == "--verbose": verbose = True
  if latex:
    latexout = codecs.open("NASummaries.tex", "w", "utf-8")
    latexHeader(latexout)
  maxshow = 0.0
  if infile is None: infile = 'NASummaries.txt'
  with codecs.open(infile, 'r', "utf-8") as x: f = x.read()
  try: os.mkdir("na")
  except Exception as e: pass
  try: os.mkdir("na/art")
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
  nobreak = False
  for summ in summs:
    if len(summ) == 0: continue
    lines = summ.split("\n")
    n = re.sub(r'^(\d+\.?\d*).*$', r'\1', lines[0])
    if art: GetAlbumArt(n)
    showdate = lines[1]
    showdate = re.sub(r'(\d+)/(\d+)/(\d+)', r'\3-\1-\2', showdate)
    if float(n) > maxshow: maxshow = float(n)
    if latex: nobreak = latexSection(latexout,lines,n,showdate,nobreak)
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
    res = os.system('xelatex -output-directory=na -halt-on-error NASummaries.tex')
    if art:
      res = os.system('xelatex -output-directory=na -halt-on-error NASummaries.tex')
    if title:
      res = os.system('xelatex -halt-on-error Title.tex')
      res = os.system('xelatex -halt-on-error Title.tex')
      res = os.system('gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite'+
                      ' -sOutputFile=na/NASummariesTitled.pdf'+
                      ' Title.pdf na/NASummaries.pdf')
      os.rename('na/NASummariesTitled.pdf', 'na/NASummaries.pdf')
    res2 = os.system('gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dNOPAUSE' +
                     ' -dQUIET -dBATCH -sOutputFile=na/NASummariesSmall.pdf' +
                     ' na/NASummaries.pdf')
    os.rename('na/NASummariesSmall.pdf', 'na/NASummaries.pdf')
    if delLtx:
      RemoveFile('NASummaries.tex')
      RemoveFile('na/NASummaries.aux')
      RemoveFile('na/NASummaries.log')
      RemoveFile('na/NASummaries.out')
      RemoveFile('na/NASummaries.idx')
      RemoveFile('na/NASummaries.ilg')
      RemoveFile('na/NASummaries.ind')
      RemoveFile('Title.log')
      RemoveFile('Title.aux')
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
      print("noop set; not executing '%s'" % (cmd))
    else:
      if verbose:
        print(cmd)
      os.system(cmd)
  if git is True:
    if shownum is not None: maxshow = shownum
    maxshow = re.sub(r'(.+?)\.0$', r'\1', str(maxshow))
    cmd = "git commit -m 'Show %s.' NASummaries.txt" % (maxshow)
    cmd2 = "git push origin master"
    if noop:
      print("noop set; not executing '%s' for %s, %s" % (cmd, shownum, maxshow))
    else:
      if verbose:
        print(cmd)
        print(cmd2)
      os.system(cmd)
      os.system(cmd2)
