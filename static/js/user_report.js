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

    var userID = document.getElementById('deleteuserID');
    userID.value = id;
}

function deleteButtonUser(){
    var userID = document.getElementById('deleteuserID').value;
    location.href =  "/deleteuseraccount?userID=" + userID;
}


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

  function setViewModalUser(userID,user_fname, user_mname, user_lname, user_birthdate, user_email, address, phone_number){
    var id = userID;

    document.getElementById("view_userID").value = userID;
    userID.value = id;
    // document.getElementById("view_user_type").value = user_type;
    document.getElementById("view_firstname").innerHTML = user_fname;
    document.getElementById("view_middlename").innerHTML = user_mname;
    document.getElementById("view_lastname").innerHTML = user_lname;
    document.getElementById("view_birthdate").value = user_birthdate;
    document.getElementById("view_email").value = user_email;
    document.getElementById("view_address").value = address;
    document.getElementById("view_phone_number").value = phone_number;
    
 

}