
import nose

nose.run(argv=['nosetests', '--tc=foo:baz', '--tests=testfoo', 
              '-vv', '--with-doctest'],
         )
