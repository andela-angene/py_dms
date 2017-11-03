import React, { PropTypes } from 'react';
import FroalaEditor from 'react-froala-wysiwyg';
import SelectInput from '../common/SelectInput';
import TextInput from '../common/TextInput';

/**
 * Document Form
 *
 * @param {Object} props { accessOptions, getContent, onChange, document, onSubmit }
 * @returns {Object} jsx object
 */
const DocumentForm = ({ accessOptions, getContent, onChange, document, onSubmit, categories }) => (
  <div className="form-div new-document">
    <div className="container">
      <h3 className="center">New Document</h3>

      <form onSubmit={onSubmit}>
        <TextInput
          name="title"
          label="Title"
          onChange={onChange}
          value={document.title}
          error={document.errors.title}
          icon="book"
        />

        <SelectInput
          value={document.category}
          name="category"
          label="Select document category"
          onChange={onChange}
          error={document.errors.category}
          options={categories}
          icon="book"
        />

        <SelectInput
          value={document.access}
          name="access"
          label="Select document access"
          onChange={onChange}
          error={document.errors.access}
          options={accessOptions}
          icon="user-plus"
        />
        <FroalaEditor
          tag="textarea"
          model={document.content}
          onModelChange={getContent}
          config={{ placeholderText: '' }}
        />
        {document.errors.content && (
          <div className="card-panel error white-text">{document.errors.content}</div>
        )}

        <div className="input-field center">
          <button className="waves-effect btn">Save</button>
        </div>
        <a id="toggleCodeIframe" className="btn-floating btn-large waves-effect waves-light teal">
          <i className="material-icons">code</i>
        </a>
        <iframe className="code-iframe" src="https://tohtml.com" width="100%" height="700px" />
      </form>
    </div>
  </div>
);

DocumentForm.propTypes = {
  accessOptions: PropTypes.array.isRequired,
  categories: PropTypes.array.isRequired,
  document: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  getContent: PropTypes.func.isRequired,
};

export default DocumentForm;
