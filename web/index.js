// not babel'd :(

const $ = document.querySelector.bind(document);

const createResultDiv = (result) => {
  const name = document.createElement('div');
  name.className = 'name'
  name.innerHTML = result.name

  const introText = document.createElement('div');
  introText.className = 'intro-text'
  introText.innerHTML = result.first_sentence

  const textWrapperDiv = document.createElement('div');

  const portrait = document.createElement('img');
  portrait.className = 'portrait'
  portrait.src = 'https://i1.sndcdn.com/artworks-000144544913-kzrf5c-t500x500.jpg'

  const portraitWrapper = document.createElement('div');
  portraitWrapper.className = 'portrait-wrapper'

  const resultEl = document.createElement('div');
  resultEl.className = 'result'
  
  textWrapperDiv.appendChild(name)
  textWrapperDiv.appendChild(introText)
  portraitWrapper.appendChild(portrait)
  resultEl.appendChild(textWrapperDiv)
  resultEl.appendChild(portraitWrapper)

  return resultEl
};

const updateResults = (results) => {
  const allResultsEl = $('.all-results');
  allResultsEl.innerHTML = '';
  results.forEach((result) => {
    allResultsEl.appendChild(createResultDiv(result));
  });
};

const identify = (query) => {
  const xhr = new XMLHttpRequest();
  xhr.open('GET', 'identify?query=' + query);
  xhr.onload = function() {
      if (xhr.status === 200) {
        updateResults(
          JSON.parse(xhr.responseText).result
        );
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
