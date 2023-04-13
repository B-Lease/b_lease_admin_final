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

  
function setViewModalAdmin(propertyID){

    document.getElementById("propertyID").value = propertyID;
}

// const modalBackdrop = document.querySelector('.modal-backdrop');
// const modal = document.querySelector('.modal');
// const openModalButton = document.querySelector('.open-modal-button');

// openModalButton.addEventListener('click', () => {
//   modalBackdrop.style.opacity = 1;
//   modal.style.display = 'block';
// });

// modal.addEventListener('click', () => {
//   modalBackdrop.style.opacity = 0;
//   modal.style.display = 'none';
// });

