def run_fortune(args=None):
    """This Function will generate random fortunes from the text file we mentioned in the FORTUNE_DIRECTORY"""  
    import subprocess

    params = ['fortune']
    if args != None:
        for i in range(0,len(args)):
            if args[i] == '-':
                params.append(args[i] + args[i+1])
            
    output = subprocess.Popen(params,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    stdout, stderr = output.communicate()
    try:
        return stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return e.output


help_fortune = textwrap.dedent(
    """ A command that displays a pseudorandom message from a database of quotations.
         Usage: fortune [-acefilsw] [-n length] [ -m pattern] [[n%] file/dir/all]

         When fortune is run with no arguments it prints out a random epigram. Epigrams are divided into several categories.

         Options and arguments: \n

         {"-a"} : Choose from all lists of maxims.

         {"-c"} : Show the cookie file from which the fortune came along with the fortune.

         {"-e"} : Consider all fortune files to be of equal size (When you have 2 or more databases of fortune files)

         {"-f"} : Print out the list of files which would be searched, but don't print a fortune.

         {"-l"} : Long dictums only. (You can verify how "long" is defined in this sense by "-n" which is be mentioned below)

         {"-m *pattern*"} : Print out all fortunes which match the basic regular expression pattern.
                            The syntax of these expressions depends on how your system defines re_comp(3) or regcomp(3), but it should nevertheless be similar to the syntax used in grep(1).

         {"-n *length*"} : Set the longest fortune length (in characters) considered to be ''short'' (the default is 160).
                           All fortunes longer than this are considered ''long''. 
                           Be careful! If you set the length too short and ask for short fortunes, or too long and ask for long ones, fortune goes into a never-ending thrash loop.

         {"-s"} : Short apothegms only. See -n on which fortunes are considered ''short''.

         {"-i"} : Ignore case for -m patterns.

         {"-w"} : Wait before termination for an amount of time calculated from the number of characters in the message. 
                  This is useful if it is executed as part of the logout procedure to guarantee that the message can be read before the screen is cleared.
    

    
        """
<<<<<<< HEAD
)



=======
)
>>>>>>> b71d134db0726b92bd7d1ba1ed024e75ec89b1c2
