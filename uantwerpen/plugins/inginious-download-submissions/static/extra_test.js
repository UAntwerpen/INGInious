function load_input_extra_test(submissionid, key, input) {
    var field = $(".problem input[name='" + key + "']");
    if(key in input)
        $(field).prop('value', input[key]);
    else
        $(field).prop('value', "");
}

function studio_init_template_extra_test(well, pid, problem)
{

}

function load_feedback_extra_test(key, content) {
    load_feedback_code(key, content);
}