$(document).ready(function() {
    $('.delete-btn').click(function() {
      var id = $(this).data('id');
      $('#delete-modal').show();
      $('.delete-confirm-btn').data('id', id);
    });
  
    $('.delete-cancel-btn').click(function() {
      $('#delete-modal').hide();
    });
  
    $('.delete-confirm-btn').click(function() {
      var id = $(this).data('id');
      location.href = location.href + "&parameter=" + value;
    });
  });

function setDeleteModalUser(deleteid){
    var id = deleteid;

    var paymentID = document.getElementById('deletepaymentID');
    paymentID.value = id;
}

function deleteButtonUser(){
    var paymentID = document.getElementById('deletepaymentID').value;
    location.href =  "/deletepaymentaccount?paymentID=" + paymentID;
}