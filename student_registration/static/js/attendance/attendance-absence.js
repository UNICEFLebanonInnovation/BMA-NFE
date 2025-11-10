

function initialise_absence_form()
{
    $(document).ready(
        function(){
            $( "#button-id-exportabsentees" ).click(function() {
                absence_export();
             }
          );
       }
    );
}

function absence_export() {
    var number_of_absences = $('#id_absence_days').val();
    var total_days = $('#id_total_days').val();
    if (number_of_absences !='' && total_days !='' ) {
       url = '/attendances/absence-export/'+number_of_absences+ '/'+ total_days;
       download(url);

    }
    else
    {
        showModal('Number Of Absences is mandatory')
    }

}

function attendance_export() {
       url = '/attendances/attendance-export/';
       download(url);
}
function total_attendance_export() {
       url = '/attendances/total-attendance-export/';
       download(url);
}
function consecutive_absence_export() {
       url = '/attendances/consecutive-attendance-export/';
       download(url);
}


function download(link) {
  var element = document.createElement('a');
  element.setAttribute('href', link);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}
