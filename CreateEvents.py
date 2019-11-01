'''
Copyright (C) 2019, Blackboard Inc.
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of Blackboard Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY BLACKBOARD INC ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL BLACKBOARD INC. BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Created on October 30, 2019

@author: shurrey
'''

from auth import AuthToken
from events import Events

import sys
import getopt
import datetime

def main(argv):
    URL = "https://blackboard.smallworldlabs.com/services/4.0"
    UID = "13"
    GID = "27"
    CID = "31"
    
    print ('\n[main] Acquiring auth token...\n')
    authorized_session = AuthToken(URL)
    authorized_session.setToken()
    print ('\n[main] Returned token: ' + authorized_session.getToken() + '\n')

    event_handler = Events(URL, authorized_session.getToken(),UID,GID,CID)

    week = 0

    start = datetime.datetime(2019,11,20,11,0)

    while week < 52:
        end = start + datetime.timedelta(hours=1)

        print("Week: " + str(week) + " Start: " + str(start) + " End: " + str(end))

        event_handler.createEvent(str(start),str(end))

        print('EventId: ' + event_handler.getEventId())

        start = start + datetime.timedelta(weeks=1)

        week += 1
    
if __name__ == '__main__':
    main(sys.argv[1:])
