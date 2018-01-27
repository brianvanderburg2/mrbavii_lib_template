""" Tests for mrbaviirc.util """

__author__      = "Brian Allen Vanderburg II"
__copyright__   = "Copyright 2018"
__license__     = "Apache License 2.0"


from ... import util


def test_updatedoc():

    @util.updatedoc("START", "END")
    def f1():
        """TEST"""
        pass

    @util.updatedoc("START", None)
    def f2():
        """TEST"""
        pass

    @util.updatedoc(None, "END")
    def f3():
        """TEST"""
        pass

    assert f1.__doc__ == "STARTTESTEND"
    assert f2.__doc__ == "STARTTEST"
    assert f3.__doc__ == "TESTEND"

def test_common_start():
    
    set1 = [
        "\t\tHello",
        "\t\tHelp"
    ]

    set2 = [
        "Wow that's nice",
        "Won't go"
    ]

    set3 = [
        "\t Next",
        "\t  Next"
    ]

    assert util.common_start(*set1) == "\t\tHel"
    assert util.common_start(*set2) == "Wo"
    assert util.common_start(*set3) == "\t "

def strip_unneeded_whitespace():

    block1 = """

    This is a test
    This is only a test
        With an indented line

    """

    block1r = (
        "This is a test"
        "This is only a test"
        "    With an indented line"
    )

    assert util.strip_unneeded_whitespace(block1) == block1r

def test_file_mover():

    # We hijack some functions temporarily
    import shutil
    import os

    orig_move = shutil.move
    orig_unlink = os.unlink
    orig_exists = os.path.exists
    
    try:
        results = []
    
        # Perform the hihack
        def new_move(src, dst):
            results.append("move")
            results.append(src)
            results.append(dst)

        shutil.move = new_move

        def new_unlink(filename):
            results.append("unlink")
            results.append(filename)

        os.unlink = new_unlink

        def new_exists(*args):
            return True

        os.path.exists = new_exists


        # Test commit
        while results: results.pop()
        m = util.FileMover("realfile.txt", "fakefile.txt.tmp")
        m.commit()

        assert results == ["move", "fakefile.txt.tmp", "realfile.txt"]

        # Test release
        while results: results.pop()
        m = util.FileMover("realfile.txt", "fakefile.txt.tmp")
        m.release()

        assert results == ["unlink", "fakefile.txt.tmp"]

        # Test context with commit
        while results: results.pop()
        with util.FileMover("realfile.txt", "fakefile.txt.tmp") as m:
            m.commit()

        assert results == ["move", "fakefile.txt.tmp", "realfile.txt"]

        # Test context without commit
        while results: results.pop()
        with util.FileMover("realfile.txt", "fakefile.txt.tmp") as m:
            pass

        assert results == ["unlink", "fakefile.txt.tmp"]

    finally:
        # Restore hijacked functions
        shutil.move = orig_move
        os.unlink = orig_unlink
        os.path.exists = orig_exists

