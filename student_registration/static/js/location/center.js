

$(document).ready(function(){
    reorganizeForm();

//    $(document).on('change', 'select#id_ , select#id_' , function(){
//       reorganizeForm();
//    });
});


function reorganizeForm()
{

}

function load_districts(url)
{
    var value = $("#id_governorate").val();
    $.ajax({
        url: url,
        data: {
            'id_governorate': value
        },
        success: function (data) {
            $("#id_caza").html(data);
        }
    })
}

function load_cadasters(url)
{
    var value = $("#id_caza").val();
    $.ajax({
        url: url,
        data: {
            'id_district': value
        },
        success: function (data) {
            $("#id_cadaster").html(data);
        }
    })
}
