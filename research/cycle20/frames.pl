% Private stdin/stdout framing for the pinned PeTTa string interface.
:- use_module(library(http/json)).
:- use_module(library(readutil)).

cycle20_frames :-
    current_prolog_flag(argv, [Main, Library, '--silent']),
    consult(Main),
    once(load_metta_file(Library, _)),
    writeln('C20READY'), flush_output,
    repeat,
    read_line_to_string(user_input, Line),
    ( Line == end_of_file -> !
    ; atom_json_dict(Line, Request, []),
      once(process_metta_string(Request.code, _)),
      format('C20DONE ~d~n', [Request.id]), flush_output, fail
    ).
