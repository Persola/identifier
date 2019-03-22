// not babel'd :(

const $ = document.querySelector.bind(document);

const updateResults = (result) => {
  console.log(result);
};

const identify = (query) => {
  const xhr = new XMLHttpRequest();
  xhr.open('GET', 'identify?query=' + query);
  xhr.onload = function() {
      if (xhr.status === 200) {
          updateResults(xhr.responseText);
      }
      else {
          alert('Query failed.');
      }
  };
  xhr.send();
};

const handleButtonClick = () => {
  const query = $('.query').value;
  identify(query);
};
