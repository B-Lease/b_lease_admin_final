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

function setDeleteModal(deleteid){
    var id = deleteid;

    var adminID = document.getElementById('deleteadminID');
    adminID.value = id;
}

function deleteButton(){
    var adminID = document.getElementById('deleteadminID').value;
    location.href =  "/deleteaccount?adminID=" + adminID;
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

function setViewModalAdmin(adminID, admin_fname, admin_mname, admin_lname, admin_username, admin_password){
   

    document.getElementById("adminID").value = adminID;
    document.getElementById("adminIDlabel").value = adminID;
    document.getElementById("admin_fname").value = admin_fname;
    document.getElementById("admin_mname").value = admin_mname;
    document.getElementById("admin_lname").value = admin_lname;
    document.getElementById("admin_username").value = admin_username;
    document.getElementById("admin_password").value = admin_password;

}


function editProfile(){
    edit = document.getElementById("edit_profile");
    cancel = document.getElementById("cancel_edit_profile");
    confirmedit = document.getElementById("confirm_edit_profile");

    adminID = document.getElementById("adminID");
    admin_fname = document.getElementById("admin_fname");
    admin_mname = document.getElementById("admin_mname");
    admin_lname = document.getElementById("admin_lname");
    admin_username = document.getElementById("admin_username");
    admin_password = document.getElementById("admin_password");


    edit.setAttribute("hidden", true);
    cancel.removeAttribute("hidden");
    confirmedit.removeAttribute("hidden");

    admin_fname.removeAttribute("disabled");
    admin_mname.removeAttribute("disabled");
    admin_lname.removeAttribute("disabled");
    admin_username.removeAttribute("disabled");
    admin_password.removeAttribute("disabled");


    
}

function cancelEdit(){
    location.reload();
}

function emptyEdit() {
   
    admin_fname = document.getElementById("admin_fname").value;
    admin_mname = document.getElementById("admin_mname").value;
    admin_lname = document.getElementById("admin_lname").value;
    admin_username = document.getElementById("admin_username").value;
    admin_password = document.getElementById("admin_password").value;

    if (admin_fname == "" || admin_mname == "" || admin_lname == "" || admin_username == "" || admin_password == "") {
        alert("Fill all the fields!");
        return false;
    };
}
