PyLangAcq: Language acquisition research in Python
==================================================

Full documentation: [http://pylangacq.org/](http://pylangacq.org/)


Download and install
--------------------

PyLangAcq requires Python 3.4 or above.

* **The latest stable release** -- hosted at
  [PyPI](https://pypi.python.org/pypi/pylangacq)
  and therefore available via `pip`:

  ```
  $ python3 -m pip install pylangacq
  ```

  `python3` is meant to point to your Python 3 interpreter.
  Administrative privileges (e.g., `sudo` on Unix-like systems) may be required.

  The stable release version is what the full documentation describes,
  unless otherwise noted.

* **Under testing and development** -- available at the
  [GitHub repository](https://github.com/pylangacq/pylangacq)

  This version likely contains experimental code not yet documented.
  You may obtain it via `git`:

  ```
  $ git clone https://github.com/pylangacq/pylangacq.git
  $ cd pylangacq
  $ python3 setup.py install
  ```

See [changlog](changelog.md) for updates in progress.


How to cite
-----------

PyLangAcq is maintained by [Jackson Lee](http://jacksonllee.com/).
If you use PyLangAcq in your research,
please cite the following:

Lee, Jackson L., Ross Burkholder, Gallagher B. Flinn, and Emily R. Coppess. 2016.
[Working with CHAT transcripts in Python](http://jacksonllee.com/papers/lee-etal-2016-pylangacq.pdf).
Technical report [TR-2016-02](http://www.cs.uchicago.edu/research/publications/techreports/TR-2016-02),
Department of Computer Science, University of Chicago.

    @TechReport{lee-et-al-pylangacq:2016,
      Title       = {Working with CHAT transcripts in Python},
      Author      = {Lee, Jackson L. and Burkholder, Ross and Flinn, Gallagher B. and Coppess, Emily R.},
      Institution = {Department of Computer Science, University of Chicago},
      Year        = {2016},
      Number      = {TR-2016-02},
    }


Syntax highlighting for CHAT transcripts
----------------------------------------

See the directory [`chat-syntax-highlighting`](chat-syntax-highlighting).


License
-------

See [license](license.txt)
