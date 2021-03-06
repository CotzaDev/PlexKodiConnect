# -*- coding: utf-8 -*-
from logging import getLogger
from threading import Thread, Lock

from xbmc import sleep

from utils import ThreadMethodsAdditionalStop, ThreadMethods, language as lang

###############################################################################

log = getLogger("PLEX."+__name__)

GET_METADATA_COUNT = 0
PROCESS_METADATA_COUNT = 0
PROCESSING_VIEW_NAME = ''
LOCK = Lock()

###############################################################################


@ThreadMethodsAdditionalStop('suspend_LibraryThread')
@ThreadMethods
class Threaded_Show_Sync_Info(Thread):
    """
    Threaded class to show the Kodi statusbar of the metadata download.

    Input:
        dialog       xbmcgui.DialogProgressBG() object to show progress
        total:       Total number of items to get
    """
    def __init__(self, dialog, total, item_type):
        self.total = total
        self.dialog = dialog
        self.item_type = item_type
        Thread.__init__(self)

    def run(self):
        """
        Catch all exceptions and log them
        """
        try:
            self.__run()
        except Exception as e:
            log.error('Exception %s' % e)
            import traceback
            log.error("Traceback:\n%s" % traceback.format_exc())

    def __run(self):
        """
        Do the work
        """
        log.debug('Show sync info thread started')
        # cache local variables because it's faster
        total = self.total
        dialog = self.dialog
        threadStopped = self.threadStopped
        dialog.create("%s: Sync %s: %s items"
                      % (lang(29999), self.item_type, str(total)),
                      "Starting")

        total = 2 * total
        totalProgress = 0
        while threadStopped() is False:
            with LOCK:
                get_progress = GET_METADATA_COUNT
                process_progress = PROCESS_METADATA_COUNT
                viewName = PROCESSING_VIEW_NAME
            totalProgress = get_progress + process_progress
            try:
                percentage = int(float(totalProgress) / float(total)*100.0)
            except ZeroDivisionError:
                percentage = 0
            dialog.update(percentage,
                          message="%s downloaded. %s processed: %s"
                                  % (get_progress,
                                     process_progress,
                                     viewName))
            # Sleep for x milliseconds
            sleep(200)
        dialog.close()
        log.debug('Show sync info thread terminated')
