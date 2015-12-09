Change log
==========

- Version 0.3 DATE????

    * Following the conventional CHILDES and CHAT terminology, the `metadata` method in `Reader` is renamed `headers` (though a "new" `metadata` method is defined and points to `headers` for convenience).

- Version 0.2 2015-12-05

    * new methods for class `Reader`: `languages`, `date`, `participants`, `participant_codes`

- Version 0.1 2015-12-04

    * first commit; set up the `chat` submodule
    * class `Reader` defined for reading `.cha` files, with methods `cha_lines`, `metadata`, and `age`

