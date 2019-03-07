// not babel'd :(

const $ = document.querySelector.bind(document);

const handleButtonClick = () => {
  const query = $('.query').value;
  console.log(`button clicked! ${query}`);
}
