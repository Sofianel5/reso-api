import serialize from 'form-serialize';

const formData = serialize(formNode, { hash: true });

const apiData = { start-time: formData.start_time, end-time: formData.end_time, closed: formData.closed };

const json = JSON.stringify(apiData);