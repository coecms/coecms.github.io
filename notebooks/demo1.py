import logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
# We disabled the existing handlers after import logging so we can configure the root logger as we want
# We set the level to DEBUG!
logging.basicConfig(level=logging.INFO)


def log_demo(level):
    # start a logger
    mylog = logging.getLogger('mylogger')
    # set the level passed as input, has to be logging.LEVEL
    mylog.setLevel(level)
    
    # add a handler to send INFO level messages to console
    
    # add a handler to send DEBUG level messages to file    
    file_handler = logging.FileHandler('mycode_debug.log','w') 
    file_handler.setLevel(logging.DEBUG)
    # set a formatter to manage the output format of our handler
    formatter = logging.Formatter('%(asctime)s | %(name)s |  %(levelname)s: %(message)s')
    file_handler.setFormatter(formatter)
    mylog.addHandler(file_handler)
    
    mylog.info('This function is a logging demo')
    # add some debug messages
    var1 = 1
    var2 = '0'
    mylog.debug('Input values are %s %s, their respective types are %s and %s', var1, var2, type(var1), type(var2))
    mylog.info('Code ends here!')
log_demo(logging.DEBUG)
