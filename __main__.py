try:
    from driver import *
except ImportError as e:
    from .driver import *

main()
