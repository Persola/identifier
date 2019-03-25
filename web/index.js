// not babel'd :(

const $ = document.querySelector.bind(document);

const createResultDiv = (result) => {
  const name = document.createElement('div');
  name.className = 'name'
  name.innerHTML = result.name

  const introText = document.createElement('div');
  introText.className = 'intro-text'
  introText.innerHTML = result.first_sentence

  const linkEl = document.createElement('a');
  linkEl.className = 'result-link'
  linkEl.href = 'https://en.wikipedia.org/wiki/' + result.name.replace(' ', '_')

  const fadeMaskEl = document.createElement('div');
  fadeMaskEl.className = 'fade-mask'

  const resultEl = document.createElement('div');
  resultEl.className = 'result'  

  resultEl.appendChild(name)
  resultEl.appendChild(introText)
  resultEl.appendChild(fadeMaskEl)
  linkEl.appendChild(resultEl)

  return linkEl
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

const displayLoadingMessage = () => {
  const loadMessageEl = document.createElement('div');
  loadMessageEl.className = 'loading-message'
  loadMessageEl.innerHTML = 'loading'
  const allResultsEl = $('.all-results');
  allResultsEl.innerHTML = '';
  allResultsEl.appendChild(loadMessageEl);
};

const handleButtonClick = () => {
  displayLoadingMessage();
  const query = $('.query').value;
  identify(query);
};
