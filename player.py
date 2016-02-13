import threading
from multiprocessing import Queue
import gi
from gi.repository import Gst, GObject
gi.require_version('Gst', '1.0')


GObject.threads_init()
Gst.init(None)

class Player(threading.Thread):

    statemap = {Gst.State.PLAYING: 'playing', Gst.State.PAUSED: 'paused', Gst.State.READY: 'stopped', Gst.State.NULL: 'null'}

    wanted_msgs = Gst.MessageType.STATE_CHANGED | Gst.MessageType.ERROR | Gst.MessageType.EOS | Gst.MessageType.DURATION_CHANGED |Gst.MessageType.BUFFERING | Gst.MessageType.CLOCK_LOST | Gst.MessageType.TAG | Gst.MessageType.ASYNC_DONE

    def __init__(self):
        super(Player, self).__init__()

        self.playbin = Gst.ElementFactory.make('playbin', 'playbin')
        self.running = True
        self.msgtimeout = 2
        self.currduration = 0

        self.queue = None
        self.start()

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, tb):
        try:
            self.close()
        except:
            print('couldnt close player')

        ''' dont always return True as it swallows all exceptions within context manger context '''
        return False


    def getqueue(self):
        if not self.queue:
            self.queue = Queue()
        return self.queue

    def postmsg(self, type, data=None):
        if self.queue:
            self.queue.put((type, data))

    def run(self):

        bus = self.playbin.get_bus()

        while self.running:
            msg = bus.timed_pop_filtered(self.msgtimeout * Gst.MSECOND, self.wanted_msgs)

            if msg is None:
                continue

            if msg.type is Gst.MessageType.STATE_CHANGED:
                old_state, new_state, pending_state = msg.parse_state_changed()
                self.postmsg(msg.type, (old_state, new_state, pending_state))

            elif msg.type is Gst.MessageType.ERROR:
                err, debug = msg.parse_error()
                self.postmsg(msg.type, (err, debug, msg.src.get_name()))

            elif msg.type is Gst.MessageType.EOS:

                self.postmsg(msg.type)

            elif msg.type is Gst.MessageType.BUFFERING:

                self.postmsg(msg.type, msg.parse_buffering())

            elif msg.type is Gst.MessageType.CLOCK_LOST:
                self.pause()                    
                self.play()
                self.postmsg(Gst.MessageType.CLOCK_LOST)
                

            elif msg.type is Gst.MessageType.DURATION_CHANGED:
                self.currduration = self.playbin.query_duration(Gst.Format.TIME)
                self.postmsg(msg.type, self.currduration)
            
            elif msg.type is Gst.MessageType.TAG:

                # the gstreamer api around the tags seems to be unstable and 
                # differs between versions so leave this out for now.
                '''
                print 'got tags info'
                
                taglist = msg.parse_tag()
                tagdict = {key: taglist[key] for key in taglist}
                
                print(tagdict)

                self.postmsg(msg.type, tagdict)
                '''
                
            
            elif msg.type is Gst.MessageType.ASYNC_DONE:

                #print 'async done'
                self.postmsg(msg.type)

            else:
                print('unexpected message of type ' % msg.type)

            

    def play(self, uri):
        self.playbin.set_property("uri", uri)
        self.playbin.set_state(Gst.State.PLAYING)

    def pause(self):
        return self.playbin.set_state(Gst.State.PAUSED)

    def resume(self):
        return self.playbin.set_state(Gst.State.PLAYING)

    def stop(self):
        return self.playbin.set_state(Gst.State.READY)
    
    @property
    def volume(self):
        return self.playbin.get_property("volume");

    @volume.setter
    def volume(self, level):
        self.playbin.set_property("volume", level);

    @property
    def playstate(self):
        old, curr, pend = self.playbin.get_state(timeout=2)
        return curr.value_nick

    @property
    def uri(self):
        return self.playbin.get_property('current-uri')

    @property
    def duration(self):
        return self.currduration


    def close(self):

        self.running = False
        self.playbin.set_state(Gst.State.NULL)
        
        if threading.current_thread() == self:
            raise Exception("attempt to join thread in own context, would cause deadlock.")
        self.join()


if __name__ == '__main__':
    import time
    with Player() as p:

        p.play('http://live-radio01.mediahubaustralia.com/2TJW/mp3/')
        for i in reversed(xrange(10)):
            
            p.volume = i
            print(p.volume)
            time.sleep(1)
