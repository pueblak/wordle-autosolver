try:
    from driver import main
except ImportError:
    from .driver import main

main()
