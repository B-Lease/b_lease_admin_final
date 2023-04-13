$(document).ready(function() {
    $('.view-btn').click(function() {
      var id = $(this).data('id');
      $('#view-modal').show();
    //   $('.v\-confirm-btn').data('id', id);
    });
  
    $('.view-cancel-btn').click(function() {
      $('#view-modal').hide();
    });
  
    // $('.delete-confirm-btn').click(function() {
    //   var id = $(this).data('id');
    //   location.href = location.href + "&parameter=" + value;
    // });
  });

  function setViewModalUser(leasing_status){
   

    document.getElementById("leasing_status").value = leasing_status;


}