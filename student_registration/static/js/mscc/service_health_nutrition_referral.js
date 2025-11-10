

$(document).ready(function(){

    reorganizeForm();
    $(document).on('change', 'select#id_referred_development_delays, select#id_referred_malnutrition, select#id_referred_anc_pnc, select#id_women_child_referred_iycf,select#id_infant_child_referred_iycf' , function(){
       reorganizeForm();
    });
});


function reorganizeForm() {
    var referred_development_delays = $('select#id_referred_development_delays').val();
    if(referred_development_delays == 'Yes'){
        $('div#div_id_development_delays').removeClass('d-none');
        if ($('#id_development_delays').val()== null || $('#id_development_delays').val()=='')
        {
            $('#id_development_delays').addClass('error-field');
        }
    }
    else{
        $('div#div_id_development_delays').addClass('d-none');
        $('#id_development_delays').removeClass('error-field');
    }

    var referred_malnutrition = $('select#id_referred_malnutrition').val();
    if( referred_malnutrition == 'Yes'){
        $('div#div_id_malnutrition_treatment_center').removeClass('d-none');
        if ($('#id_malnutrition_treatment_center').val()== null || $('#id_malnutrition_treatment_center').val()=='')
        {
            $('#id_malnutrition_treatment_center').addClass('error-field');
        }
    }
    else{
        $('div#div_id_malnutrition_treatment_center').addClass('d-none');
        $('#id_malnutrition_treatment_center').removeClass('error-field');
    }

    var  referred_anc_pnc = $('select#id_referred_anc_pnc').val();
    if(  referred_anc_pnc == 'Yes'){
        $('div#div_id_phc_center').removeClass('d-none');
        if ($('#id_phc_center').val()== null || $('#id_phc_center').val()=='')
        {
            $('#id_phc_center').addClass('error-field');
        }
    }
    else{
        $('div#div_id_phc_center').addClass('d-none');
        $('#id_phc_center').removeClass('error-field');
    }

    var  women_child_referred_iycf = $('select#id_women_child_referred_iycf').val();
    if( women_child_referred_iycf  == 'Yes'){
        $('div#div_id_women_child_referred_organization').removeClass('d-none');
        if ($('#id_women_child_referred_organization').val()== null || $('#id_women_child_referred_organization').val()=='')
        {
            $('#id_women_child_referred_organization').addClass('error-field');
        }
    }
    else{
        $('div#div_id_women_child_referred_organization').addClass('d-none');
        $('#id_women_child_referred_organization').removeClass('error-field');
    }

    var infant_child_referred_iycf  = $('select#id_infant_child_referred_iycf').val();
    if( infant_child_referred_iycf == 'Yes'){
        $('div#div_id_infant_child_referred_organization').removeClass('d-none');
        if ($('#id_infant_child_referred_organization').val()== null || $('#id_infant_child_referred_organization').val()=='')
        {
            $('#id_infant_child_referred_organization').addClass('error-field');
        }
    }
    else{
        $('div#div_id_infant_child_referred_organization').addClass('d-none');
        $('#id_infant_child_referred_organization').removeClass('error-field');
    }

  }

