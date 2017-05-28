import os
import re

graph_search = re.compile(r'includegraphics\[?.*\]?\{(.*)\}')
input_search = re.compile(r'input\{(.*)\}')
bib_search = re.compile(r'bibliography\{(.*)\}')
bibstyle_search = re.compile(r'bibliographystyle\{(.*)\}')

def do_tex(filename, fignum, AAdir='AAS_tex'):

    with open(filename,'r') as f:
        lines = f.readlines()

    #We're going to write all lines to a new file
    with open('{}/{}'.format(AAdir,filename),'w') as nf:
        
        for l in lines:

            #Look for graphics
            if r'\includegraphics' in l and l.split()[0] != '%':
                print l
                g = graph_search.search(l)
                plot_file = g.group(1)
                
                #Rename the file
                extension = plot_file.split('.')[-1]
                new_name = 'f{:n}.{}'.format(fignum,extension)
                print '{} -> {}/{}'.format(plot_file, AAdir, new_name)

                os.system('cp {} {}/{}'.format(plot_file, AAdir, new_name))
                l = l.replace(plot_file, new_name)

                #Increment
                fignum += 1
            
            #No matter what we found, we need to write the new line
            nf.write(l)

    return fignum

def is_comment(line):

    for t in line:
        if t == '%':
            return True
        if t not in [' ','%']:
            return False
    return False

def read_file(mainfile, keepcomment=False):

    plots = {}
    ms = []
    
    with open(mainfile, 'r') as f:
        lines = f.readlines()

    for l in lines:

        if r'\input' in l and l.split()[0] != '%':
            i = input_search.search(l)
            input_file = i.group(1)

            if input_file.split('.')[-1] != 'tex':
                input_file += '.tex'

            print "Found source file ", input_file
            nls = read_file(input_file)

            ms += nls

        #Don't re-input input lines!
        else:
            if not is_comment(l) or keepcomment:
                ms.append(l)

    return ms
            
def do_plots(ms, AAdir='AAS_tex'):

    fignum = 1
    ms_o = []
    for l in ms:

            #Look for graphics
            if r'\includegraphics' in l and l.split()[0] != '%':
                print l
                g = graph_search.search(l)
                plot_file = g.group(1)
                
                #Rename the file
                extension = plot_file.split('.')[-1]
                new_name = 'f{:n}.{}'.format(fignum,extension)
                print '{} -> {}/{}'.format(plot_file, AAdir, new_name)

                os.system('cp {} {}/{}'.format(plot_file, AAdir, new_name))
                l = l.replace(plot_file, new_name)

                #Increment
                fignum += 1

            ms_o.append(l)
                
    return ms_o

def do_bib(ms, AAdir='AAS_tex'):

    for l in ms:

        if r'\bibliographystyle{' in l and l.split()[0] != '%':

            g = bibstyle_search.search(l)
            style_file = g.group(1)

            if style_file.split('.')[-1] != 'bst':
                style_file += '.bst'

            if os.path.exists(style_file):
                os.system('cp {0} {1}/{0}'.format(style_file, AAdir))
            else:
                print "Could not find bibliography style file {}".format(style_file)
                print "Hopefully you have this in your path somewhere"

        if r'\bibliography{' in l and l.split()[0] != '%':

            g = bib_search.search(l)
            bib_file = g.group(1)

            if bib_file.split('.')[-1] != 'bib':
                bib_file += '.bib'
                
            os.system('cp {0} {1}/{0}'.format(bib_file, AAdir))

    return
                
def main(mainfile, AAdir='AAS_tex', keepcomment=False):

    if os.path.samefile(os.getcwd(),AAdir):
        print 'WARNING'

    ms = read_file(mainfile, keepcomment)
    ms = do_plots(ms,AAdir)

    do_bib(ms,AAdir)
    
    #Write final document
    with open('{}/{}'.format(AAdir,mainfile),'w') as nf:
        for l in ms:
            nf.write(l)

    print "All done!"
    return

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1]))