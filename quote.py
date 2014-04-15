#!/usr/bin/env python

# Copyright 2014 The pyrcbot Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import sqlite3
import random
import os.path

class IRCPlugin:
    def __init__(self):
        self.db_path = os.path.dirname(os.path.realpath(__file__))+'/quotes.db'
        self.helpline = ['Quote plugin help:',
            '  !quote add <nick> <quote> - Add quote',
            '  !quote search <search_term> - Search quote',
            '  !quote random - Get random quote']

        self.db = sqlite3.connect(self.db_path)
        self.dbcon = self.db.cursor()
        # Check if the DB is empty
        if len(self.dbcon.execute('SELECT name FROM sqlite_master WHERE \
            name="quotes"').fetchall()) == 0:
            print '[Quote]: db file not found. Creating db...' 
            self.create_db()

    def get_help(self):
        return '!quote help - Help for quotes plugin'

    def get_regexp(self):
        return r':(.+?)!.+? PRIVMSG (.+?) :(!quote[^\r\n]*)'

    def cmd(self, match, ircbot):
        if match.group(2) == ircbot.nick:
            dst = match.group(1)
        else:
            dst = ircbot.channel

        argv = match.group(3).split(' ')

        if argv[1] == 'help':
            map(lambda f: ircbot.privmsg(dst, f), self.helpline)
        elif argv[1] == 'add':
            self.add_quote(argv[2], ' '.join(argv[3:]))
        elif argv[1] == 'search':
            quotes = self.search_quote(' '.join(argv[2:]))
            ircbot.privmsg(dst, 'Search results:')
            map(lambda f: ircbot.privmsg(dst, '  <%s> %s' % (f[0],f[1])), quotes)
        elif argv[1] == 'random':
            ircbot.privmsg(dst, self.random_quote())
        else:
            ircbot.privmsg(dst, 'Quote: Unknown command')

    def close(self):
        print '[Quote] closing...'
        self.db.close()

    def create_db(self):
        self.dbcon.execute('CREATE TABLE quotes (nick text, quote text)')

    def add_quote(self, nick, quote):
        try:
            self.dbcon.execute('INSERT INTO quotes (nick, quote) VALUES (?,?)',
                    (nick, quote))
            self.db.commit()
        except Exception as e:
            print '[Quote] Error: %s' % e

    def search_quote(self, search_term):
        try:
            quotes = self.dbcon.execute('SELECT nick,quote FROM quotes WHERE \
                    nick LIKE :term OR quote LIKE :term',
                    {'term': '%'+search_term+'%'}).fetchall()
            return quotes;
        except Exception as e:
            print '[Quote] Error: %s' % e

    def random_quote(self):
        try:
            quotes = self.dbcon.execute('SELECT nick,quote FROM quotes').fetchall()
            quote = quotes[random.randint(0,len(quotes)-1)]
            return '<%s> %s' % (quote[0], quote[1])
        except Exception as e:
            print '[Quote] Error: %s' % e
