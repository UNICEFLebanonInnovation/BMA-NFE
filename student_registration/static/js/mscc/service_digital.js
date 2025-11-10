

$(document).ready(function(){
    reorganizeForm();

    $(document).on('change', 'select#id_using_akelius , select#id_using_lp' , function(){
       reorganizeForm();
    });
});


function reorganizeForm()
{
    var using_akelius = $('select#id_using_akelius').val();
    if(using_akelius == 'Yes'){
        $('div.akelius').removeClass('d-none');
    }
    else{
        $('div.akelius').addClass('d-none');
    }

    var using_lp = $('select#id_using_lp').val();
    if(using_lp == 'Yes'){
        $('div.lp').removeClass('d-none');
    }
    else{
        $('div.lp').addClass('d-none');
    }

  }

