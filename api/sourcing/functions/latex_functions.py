def write_deals_table(date, deals, agents, dc_status, path):
    text = DEALS_TABLE_START + date + DEALS_TABLE_MIDDLE
    for i in range(len(deals)):
        deal = deals[i]
        agent = agents[i]
        status = "Yes" if dc_status[i] else "No"
        text += f"{deal} & {status} & & \\\ "
        text += f"{agent} & & & \\\ \n\hline \n"
        if i == len(deals) - 1:
            break
        if i in (6, 13, 20):
            text += r'''\end{tabularx}'''
            text += DEALS_TABLE_MIDDLE2
    text += DEALS_TABLE_END
    with open(path, "w") as latex_file:
        latex_file.write(text)


def format_latex(s):
    s = s.replace('$', '\\$')
    return s


DEALS_TABLE_START = r'''\documentclass{article}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{tabularx}
\usepackage{geometry}
\usepackage{pdflscape}
\usepackage[table]{xcolor}
\renewcommand{\familydefault}{\sfdefault}
\geometry{a4paper, margin=1in}
\pagestyle{empty}

\definecolor{blue(pigment)}{rgb}{0.2, 0.2, 0.6}

\begin{document}
\begin{landscape}
\begin{center}
\textbf{\fontsize{14}{17}\selectfont Canadian PE Ownership Changes - Canadian Target} \par
\medskip
\fontsize{12}{14}
\selectfont
'''

DEALS_TABLE_MIDDLE = r'''\end{center}

\fontsize{7}{12}\selectfont
\renewcommand{\arraystretch}{1.5}
\begin{tabularx}{\linewidth}{|X|p{1.9cm}|p{3.2cm}|p{3.35cm}|}
\hline
\rowcolor{blue(pigment)!80}
{\color{white}\textbf{Deal}} & {\color{white}\textbf{In DealCloud}} & {\color{white}\textbf{Reviewed by Birch Hill}} & 
{\color{white}\textbf{In Market for Birch Hill}} \\
\hline
'''

DEALS_TABLE_MIDDLE2 = r'''\fontsize{7}{12}\selectfont
\renewcommand{\arraystretch}{1.5}
\begin{tabularx}{\linewidth}{|X|p{1.9cm}|p{3.2cm}|p{3.35cm}|}
\hline
\rowcolor{blue(pigment)!80}
{\color{white}\textbf{Deal}} & {\color{white}\textbf{In DealCloud}} & {\color{white}\textbf{Reviewed by Birch Hill}} & 
{\color{white}\textbf{In Market for Birch Hill}} \\
\hline
'''

DEALS_TABLE_END = r'''\end{tabularx}
\end{landscape}
\end{document}
'''