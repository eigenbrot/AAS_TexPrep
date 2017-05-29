#!/usr/bin/python
import os
import re

graph_search = re.compile(r'includegraphics\[?.*\]?\{(.*)\}')
input_search = re.compile(r'input\{(.*)\}')
bib_search = re.compile(r'bibliography\{(.*)\}')
bibstyle_search = re.compile(r'bibliographystyle\{(.*)\}')

def is_comment(line):
    '''Return true if a line is a tex comment

    NOTE: As long as there is one non-whitespace, non comment
    character in the line then it is NOT a comment.

    For example:
      '    %%% test' - is a comment
      '  t%est' - is NOT a comment
    '''

    for t in line:
        if t == '%':
            return True
        if t not in [' ','%']:
            return False
    return False

def read_file(mainfile, keepcomment=False):
    '''Read an entire manuscript into memory as a list of lines.

    This will step through any \include statements and keep everything
    in order.
    '''

    ms = []
    
    with open(mainfile, 'r') as f:
        lines = f.readlines()

    for l in lines:

        if r'\input' in l and l.split()[0] != '%':
            #Find the name of the input file
            i = input_search.search(l)
            input_file = i.group(1)

            if input_file.split('.')[-1] != 'tex':
                input_file += '.tex'

            #Read the input file. Recursion!
            print "Found source file ", input_file
            nls = read_file(input_file, keepcomment)

            ms += nls

        #The else ensures we don't double each input
        # by re-copying the \input statement
        else:
            if not is_comment(l) or keepcomment:
                ms.append(l)

    return ms
            
def do_plots(ms, AAdir='AAS_tex'):
    '''Rename plots and references to sequential f? files

    This should work no matter the graphic format. Any non-commented
    \includegraphics lines will be parsed.
    '''

    fignum = 1
    ms_o = [] #The modified manuscript lines.
              # Because l.replace doesn't work inplace (lame)
    for l in ms:

            #Look for graphics
            if r'\includegraphics' in l and l.split()[0] != '%':
                g = graph_search.search(l)
                plot_file = g.group(1)
                
                #Rename the file
                extension = plot_file.split('.')[-1]
                new_name = 'f{:n}.{}'.format(fignum,extension)
                print '{} -> {}/{}'.format(plot_file, AAdir, new_name)

                #Copy the file to the output directory
                os.system('cp {} {}/{}'.format(plot_file, AAdir, new_name))
                l = l.replace(plot_file, new_name)

                #Increment
                fignum += 1

            ms_o.append(l)
                
    return ms_o

def do_bib(ms, AAdir='AAS_tex'):
    '''Look for latex bibliography inputs and copy the needed files.

    Copying the style file isn't strictly necessary for AAS uploads,
    but having it in the output directory makes it easy to check that
    the modified source still builds the correct document.
    '''
    
    for l in ms:

        #Look for style files. Not sure why we do this first, w/e.
        if r'\bibliographystyle{' in l and l.split()[0] != '%':

            g = bibstyle_search.search(l)
            style_file = g.group(1)

            #Does the input to bibliographystyle ever have the
            # extension? I'm not sure.
            if style_file.split('.')[-1] != 'bst':
                style_file += '.bst'

            if os.path.exists(style_file):
                os.system('cp {0} {1}/{0}'.format(style_file, AAdir))
            else:
                #No big deal, but we'll warn the user nontheless
                print "Could not find bibliography style file {}".format(style_file)
                print "Hopefully you have this in your path somewhere"

        #Look for the bibliography database
        if r'\bibliography{' in l and l.split()[0] != '%':

            g = bib_search.search(l)
            bib_file = g.group(1)

            if bib_file.split('.')[-1] != 'bib':
                bib_file += '.bib'
                
            os.system('cp {0} {1}/{0}'.format(bib_file, AAdir))

    return

def parse_input(inputlist):
    """Parse arguments given to this module by the shell into useful function arguments and options

    Parameters
    ----------
    
    inputlist : list of str
        Probably sys.argv

    Returns
    -------
    """

    keepcomment = False
    AAdir = 'AAS_tex'
    samedir = False
    mainfile = ''
    
    for i, token in enumerate(inputlist):
        if token == '-k':
            keepcomment = True
        elif token == '-d':
            AAdir = inputlist[i+1]
        elif token == '--same-dir':
            samedir = True
        else:
            mainfile = inputlist[i]
            
    return mainfile, AAdir, samedir, keepcomment

def main(mainfile, AAdir='AAS_tex', keepcomment=False):
    '''A simple function to  run each step of the processing pipeline
    '''

    #ms is a list of all the lines in the input document
    # After these two steps it will (maybe) have its comments
    # removed and all the references to plot names will be
    # changed.
    ms = read_file(mainfile, keepcomment)
    ms = do_plots(ms,AAdir)

    #do_bib just copies the necessary bib files into the
    # output directory. It doesn't modify anything.
    do_bib(ms,AAdir)
    
    #Write final document
    with open('{}/{}'.format(AAdir,mainfile),'w') as nf:
        for l in ms:
            nf.write(l)

    print "All done!"
    return

def dir_warn():
    '''A simple function to warn the user that they're selected output
    directory is the same as cwd. In most cases this would cause some
    bad behavior.
    '''

    print 
    print "You've set the AAtex build directory to be the same as the current directory. This is not recommended because your original tex file will be overwritted. To force this behavior use the --same-dir option"
    print 
    
if __name__ == '__main__':
    import sys

    #My favorite error
    if len(sys.argv) <= 1:
        print "The request was made but it was not good"
        sys.exit()

    #Get the necessary arguments and options
    mainfile, AAdir, samedir, keepcomment = parse_input(sys.argv[1:])

    #Do some sanity checks...
    #
    #Does the tex file actually exist?
    if not os.path.exists(mainfile):
        raise Exception("Could not find main tex file {}. Aborting".format(mainfile))

    #Does the output directory exist?
    if os.path.exists(AAdir):
        #Is it the same as the cwd? This would be bad.
        if os.path.samefile(os.getcwd(), AAdir) and not samedir:
            dir_warn()
            sys.exit()
    else:
        #Is it the same as the cwd? 
        if os.path.abspath(os.getcwd()) == os.path.abspath(AAdir) and not samedir:
            dir_warn()
        print "Creating output directory {}".format(AAdir)
        os.makedirs(AAdir)

    #Run the program
    sys.exit(main(mainfile, AAdir, keepcomment))
