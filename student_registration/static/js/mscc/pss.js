
$(document).ready(function(){
       reorganizeForm();

    $(document).on('change', 'select#id_caregivers_distress, select#id_child_distress ' , function(){
       reorganizeForm();
    });
});


function reorganizeForm()
{
    var caregivers_distress = $('select#id_caregivers_distress').val();
    if(caregivers_distress == 'Yes'){
        $('div#div_id_caregivers_additional_parenting').removeClass('d-none');
        if ($('#id_caregivers_additional_parenting').val()== null || $('#id_caregivers_additional_parenting').val()=='')
        {
            $('#id_caregivers_additional_parenting').addClass('error-field');
        }
    }
    else{
        $('#id_caregivers_additional_parenting').val('');
        $('div#div_id_caregivers_additional_parenting').addClass('d-none');
        $('#id_caregivers_additional_parenting').removeClass('error-field');
    }

    var child_distress = $('select#id_child_distress').val();
    if(child_distress == 'Yes'){
        $('div#div_id_child_additional_parenting').removeClass('d-none');
        if ($('#id_child_additional_parenting').val()== null || $('#id_child_additional_parenting').val()=='')
        {
            $('#id_child_additional_parenting').addClass('error-field');
        }
    }
    else{
        $('#id_child_additional_parenting').val('');
        $('div#div_id_child_additional_parenting').addClass('d-none');
        $('#id_child_additional_parenting').removeClass('error-field');
    }
  }

