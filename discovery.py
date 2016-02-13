
import avahi
import dbus

class ServicePublisher(object):

    def __init__(self, name, port=5000, svctype='_http._tcp', domain='', host='', msg=''):

        self.group = None

        self.name = name
        self.port = port
        self.svctype = svctype
        self.domain = domain
        self.host = host        
        self.msg = msg

    def __enter__(self):

        self.publish()
        return self

    def __exit__(self, a, b, c):

        try:
            self.unpublish()
        except Exception as e:
            print('exception in unpublish (%s)'.format(str(e)))
            

        return False

    def publish(self):

        bus = dbus.SystemBus()

        server = dbus.Interface(
                         bus.get_object(
                                 avahi.DBUS_NAME,
                                 avahi.DBUS_PATH_SERVER),
                        avahi.DBUS_INTERFACE_SERVER)

        grp = dbus.Interface(
                    bus.get_object(avahi.DBUS_NAME,
                                   server.EntryGroupNew()),
                    avahi.DBUS_INTERFACE_ENTRY_GROUP)

        grp.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC,dbus.UInt32(0),
                     self.name, self.svctype, self.domain, self.host,
                     dbus.UInt16(self.port), self.msg)

        grp.Commit()
        self.group = grp
        print('advertising avahi service')

    def unpublish(self):

        print('stop advertising avahi service')
        self.group.Reset()