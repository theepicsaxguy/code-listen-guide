================================================
FILE: docs/usage/advanced_options.md
================================================
## Model prefetching and offline usage

By default, models are downloaded automatically upon first usage. If you would prefer
to explicitly prefetch them for offline use (e.g. in air-gapped environments) you can do
that as follows:

**Step 1: Prefetch the models**

Use the `chonkie-tools models download` utility:

```sh
$ chonkie-tools models download
Downloading layout model...
Downloading tableformer model...
Downloading picture classifier model...
Downloading code formula model...
Downloading easyocr models...
Models downloaded into $HOME/.cache/chonkie/models.
```

Alternatively, models can be programmatically downloaded using `chonkie.utils.model_downloader.download_models()`.

Also, you can use `download-hf-repo` parameter to download arbitrary models from HuggingFace by specifying repo id:

```sh
$ chonkie-tools models download-hf-repo ds4sd/Smolchonkie-256M-preview
Downloading ds4sd/Smolchonkie-256M-preview model from HuggingFace...
```

**Step 2: Use the prefetched models**

```python
from chonkie.datamodel.base_models import InputFormat
from chonkie.datamodel.pipeline_options import EasyOcrOptions, PdfPipelineOptions
from chonkie.document_converter import DocumentConverter, PdfFormatOption

artifacts_path = "/local/path/to/models"

pipeline_options = PdfPipelineOptions(artifacts_path=artifacts_path)
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

Or using the CLI:

```sh
chonkie --artifacts-path="/local/path/to/models" FILE
```

Or using the `chonkie_ARTIFACTS_PATH` environment variable:

```sh
export chonkie_ARTIFACTS_PATH="/local/path/to/models"
python my_chonkie_script.py
```

## Using remote services

The main purpose of chonkie is to run local models which are not sharing any user data with remote services.
Anyhow, there are valid use cases for processing part of the pipeline using remote services, for example invoking OCR engines from cloud vendors or the usage of hosted LLMs.

In chonkie we decided to allow such models, but we require the user to explicitly opt-in in communicating with external services.

```py
from chonkie.datamodel.base_models import InputFormat
from chonkie.datamodel.pipeline_options import PdfPipelineOptions
from chonkie.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions(enable_remote_services=True)
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

When the value `enable_remote_services=True` is not set, the system will raise an exception `OperationNotAllowed()`.

_Note: This option is only related to the system sending user data to remote services. Control of pulling data (e.g. model weights) follows the logic described in [Model prefetching and offline usage](#model-prefetching-and-offline-usage)._

### List of remote model services

The options in this list require the explicit `enable_remote_services=True` when processing the documents.

- `PictureDescriptionApiOptions`: Using vision models via API calls.


## Adjust pipeline features

The example file [custom_convert.py](../examples/custom_convert.py) contains multiple ways
one can adjust the conversion pipeline and features.

### Control PDF table extraction options

You can control if table structure recognition should map the recognized structure back to PDF cells (default) or use text cells from the structure prediction itself.
This can improve output quality if you find that multiple columns in extracted tables are erroneously merged into one.


```python
from chonkie.datamodel.base_models import InputFormat
from chonkie.document_converter import DocumentConverter, PdfFormatOption
from chonkie.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.do_cell_matching = False  # uses text cells predicted from table structure model

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

Since chonkie 1.16.0: You can control which TableFormer mode you want to use. Choose between `TableFormerMode.FAST` (faster but less accurate) and `TableFormerMode.ACCURATE` (default) to receive better quality with difficult table structures.

```python
from chonkie.datamodel.base_models import InputFormat
from chonkie.document_converter import DocumentConverter, PdfFormatOption
from chonkie.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE  # use more accurate TableFormer model

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```


## Impose limits on the document size

You can limit the file size and number of pages which should be allowed to process per document:

```python
from pathlib import Path
from chonkie.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"
converter = DocumentConverter()
result = converter.convert(source, max_num_pages=100, max_file_size=20971520)
```

## Convert from binary PDF streams

You can convert PDFs from a binary stream instead of from the filesystem as follows:

```python
from io import BytesIO
from chonkie.datamodel.base_models import DocumentStream
from chonkie.document_converter import DocumentConverter

buf = BytesIO(your_binary_stream)
source = DocumentStream(name="my_doc.pdf", stream=buf)
converter = DocumentConverter()
result = converter.convert(source)
```

## Limit resource usage

You can limit the CPU threads used by chonkie by setting the environment variable `OMP_NUM_THREADS` accordingly. The default setting is using 4 CPU threads.


## Use specific backend converters

!!! note

    This section discusses directly invoking a [backend](../concepts/architecture.md),
    i.e. using a low-level API. This should only be done when necessary. For most cases,
    using a `DocumentConverter` (high-level API) as discussed in the sections above
    should suffice — and is the recommended way.

By default, chonkie will try to identify the document format to apply the appropriate conversion backend (see the list of [supported formats](supported_formats.md)).
You can restrict the `DocumentConverter` to a set of allowed document formats, as shown in the [Multi-format conversion](../examples/run_with_formats.py) example.
Alternatively, you can also use the specific backend that matches your document content. For instance, you can use `HTMLDocumentBackend` for HTML pages:

```python
import urllib.request
from io import BytesIO
from chonkie.backend.html_backend import HTMLDocumentBackend
from chonkie.datamodel.base_models import InputFormat
from chonkie.datamodel.document import InputDocument

url = "https://en.wikipedia.org/wiki/Duck"
text = urllib.request.urlopen(url).read()
in_doc = InputDocument(
    path_or_stream=BytesIO(text),
    format=InputFormat.HTML,
    backend=HTMLDocumentBackend,
    filename="duck.html",
)
backend = HTMLDocumentBackend(in_doc=in_doc, path_or_stream=BytesIO(text))
dl_doc = backend.convert()
print(dl_doc.export_to_markdown())
```



================================================
FILE: docs/usage/enrichments.md
================================================
chonkie allows to enrich the conversion pipeline with additional steps which process specific document components,
e.g. code blocks, pictures, etc. The extra steps usually require extra models executions which may increase
the processing time consistently. For this reason most enrichment models are disabled by default.

The following table provides an overview of the default enrichment models available in chonkie.

| Feature | Parameter | Processed item | Description |
| ------- | --------- | ---------------| ----------- |
| Code understanding | `do_code_enrichment` | `CodeItem` | See [docs below](#code-understanding). |
| Formula understanding | `do_formula_enrichment` | `TextItem` with label `FORMULA` | See [docs below](#formula-understanding). |
| Picture classification | `do_picture_classification` | `PictureItem` | See [docs below](#picture-classification). |
| Picture description | `do_picture_description` | `PictureItem` | See [docs below](#picture-description). |


## Enrichments details

### Code understanding

The code understanding step allows to use advanced parsing for code blocks found in the document.
This enrichment model also set the `code_language` property of the `CodeItem`.

Model specs: see the [`CodeFormula` model card](https://huggingface.co/ds4sd/CodeFormula).

Example command line:

```sh
chonkie --enrich-code FILE
```

Example code:

```py
from chonkie.document_converter import DocumentConverter, PdfFormatOption
from chonkie.datamodel.pipeline_options import PdfPipelineOptions
from chonkie.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.do_code_enrichment = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("https://arxiv.org/pdf/2501.17887")
doc = result.document
```

### Formula understanding

The formula understanding step will analize the equation formulas in documents and extract their LaTeX representation.
The HTML export functions in the chonkieDocument will leverage the formula and visualize the result using the mathml html syntax.

Model specs: see the [`CodeFormula` model card](https://huggingface.co/ds4sd/CodeFormula).

Example command line:

```sh
chonkie --enrich-formula FILE
```

Example code:

```py
from chonkie.document_converter import DocumentConverter, PdfFormatOption
from chonkie.datamodel.pipeline_options import PdfPipelineOptions
from chonkie.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.do_formula_enrichment = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("https://arxiv.org/pdf/2501.17887")
doc = result.document
```

### Picture classification

The picture classification step classifies the `PictureItem` elements in the document with the `DocumentFigureClassifier` model.
This model is specialized to understand the classes of pictures found in documents, e.g. different chart types, flow diagrams,
logos, signatures, etc.

Model specs: see the [`DocumentFigureClassifier` model card](https://huggingface.co/ds4sd/DocumentFigureClassifier).

Example command line:

```sh
chonkie --enrich-picture-classes FILE
```

Example code:

```py
from chonkie.document_converter import DocumentConverter, PdfFormatOption
from chonkie.datamodel.pipeline_options import PdfPipelineOptions
from chonkie.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.generate_picture_images = True
pipeline_options.images_scale = 2
pipeline_options.do_picture_classification = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("https://arxiv.org/pdf/2501.17887")
doc = result.document
```


### Picture description

The picture description step allows to annotate a picture with a vision model. This is also known as a "captioning" task.
The chonkie pipeline allows to load and run models completely locally as well as connecting to remote API which support the chat template.
Below follow a few examples on how to use some common vision model and remote services.


```py
from chonkie.document_converter import DocumentConverter, PdfFormatOption
from chonkie.datamodel.pipeline_options import PdfPipelineOptions
from chonkie.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.do_picture_description = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("https://arxiv.org/pdf/2501.17887")
doc = result.document

```

#### Granite Vision model

Model specs: see the [`ibm-granite/granite-vision-3.1-2b-preview` model card](https://huggingface.co/ibm-granite/granite-vision-3.1-2b-preview).

Usage in chonkie:

```py
from chonkie.datamodel.pipeline_options import granite_picture_description

pipeline_options.picture_description_options = granite_picture_description
```

#### SmolVLM model

Model specs: see the [`HuggingFaceTB/SmolVLM-256M-Instruct` model card](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct).

Usage in chonkie:

```py
from chonkie.datamodel.pipeline_options import smolvlm_picture_description

pipeline_options.picture_description_options = smolvlm_picture_description
```

#### Other vision models

The option class `PictureDescriptionVlmOptions` allows to use any another model from the Hugging Face Hub.

```py
from chonkie.datamodel.pipeline_options import PictureDescriptionVlmOptions

pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
    repo_id="",  # <-- add here the Hugging Face repo_id of your favorite VLM
    prompt="Describe the image in three sentences. Be concise and accurate.",
)
```

#### Remote vision model

The option class `PictureDescriptionApiOptions` allows to use models hosted on remote platforms, e.g.
on local endpoints served by [VLLM](https://docs.vllm.ai), [Ollama](https://ollama.com/) and others,
or cloud providers like [IBM watsonx.ai](https://www.ibm.com/products/watsonx-ai), etc.

_Note: in most cases this option will send your data to the remote service provider._

Usage in chonkie:

```py
from chonkie.datamodel.pipeline_options import PictureDescriptionApiOptions

# Enable connections to remote services
pipeline_options.enable_remote_services=True  # <-- this is required!

# Example using a model running locally, e.g. via VLLM
# $ vllm serve MODEL_NAME
pipeline_options.picture_description_options = PictureDescriptionApiOptions(
    url="http://localhost:8000/v1/chat/completions",
    params=dict(
        model="MODEL NAME",
        seed=42,
        max_completion_tokens=200,
    ),
    prompt="Describe the image in three sentences. Be consise and accurate.",
    timeout=90,
)
```

End-to-end code snippets for cloud providers are available in the examples section:

- [IBM watsonx.ai](../examples/pictures_description_api.py)


## Develop new enrichment models

Besides looking at the implementation of all the models listed above, the chonkie documentation has a few examples
dedicated to the implementation of enrichment models.

- [Develop picture enrichment](../examples/develop_picture_enrichment.py)
- [Develop formula enrichment](../examples/develop_formula_understanding.py)



================================================
FILE: docs/usage/index.md
================================================
## Basic usage

### Python

In chonkie, working with documents is as simple as:

1. converting your source file to a chonkie document
2. using that chonkie document for your workflow

For example, the snippet below shows conversion with export to Markdown:

```python
from chonkie.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"  # file path or URL
converter = DocumentConverter()
doc = converter.convert(source).document

print(doc.export_to_markdown())  # output: "### chonkie Technical Report[...]"
```

chonkie supports a wide array of [file formats](./supported_formats.md) and, as outlined in the
[architecture](../concepts/architecture.md) guide, provides a versatile document model along with a full suite of
supported operations.

### CLI

You can additionally use chonkie directly from your terminal, for instance:

```console
chonkie https://arxiv.org/pdf/2206.01062
```

The CLI provides various options, such as 🥚[Granitechonkie](https://huggingface.co/ibm-granite/granite-chonkie-258M) (incl. MLX acceleration) & other VLMs:
```bash
chonkie --pipeline vlm --vlm-model granite_chonkie https://arxiv.org/pdf/2206.01062
```

For all available options, run `chonkie --help` or check the [CLI reference](../reference/cli.md).

## What's next

Check out the Usage subpages (navigation menu on the left) as well as our [featured examples](../examples/index.md) for
additional usage workflows, including conversion customization, RAG, framework integrations, chunking, serialization,
enrichments, and much more!



================================================
FILE: docs/usage/jobkit.md
================================================
chonkie's document conversion can be executed as distributed jobs using [chonkie Jobkit](https://github.com/chonkie-project/chonkie-jobkit).

This library provides:

- Pipelines for running jobs with Kueflow pipelines, Ray, or locally.
- Connectors to import and export documents via HTTP endpoints, S3, or Google Drive.

## Usage

### CLI

You can run Jobkit locally via the CLI:

```sh
uv run chonkie-jobkit-local [configuration-file-path]
```

The configuration file defines:

- chonkie conversion options (e.g. OCR settings)
- Source location of input documents
- Target location for the converted outputs

Example configuration file:

```yaml
options:               # Example chonkie's conversion options
  do_ocr: false         
sources:               # Source location (here Google Drive)
  - kind: google_drive
    path_id: 1X6B3j7GWlHfIPSF9VUkasN-z49yo1sGFA9xv55L2hSE
    token_path: "./dev/google_drive/google_drive_token.json" 
    credentials_path: "./dev/google_drive/google_drive_credentials.json"  
target:                # Target location (here S3)
  kind: s3
  endpoint: localhost:9000
  verify_ssl: false
  bucket: chonkie-target
  access_key: minioadmin
  secret_key: minioadmin
```

## Connectors

Connectors are used to import documents for processing with chonkie and to export results after conversion.

The currently supported connectors are:

- HTTP endpoints
- S3
- Google Drive

### Google Drive

To use Google Drive as a source or target, you need to enable the API and set up credentials.

Step 1: Enable the [Google Drive API](https://console.cloud.google.com/apis/enableflow?apiid=drive.googleapis.com).

- Go to the Google [Cloud Console](https://console.cloud.google.com/).
- Search for “Google Drive API” and enable it.

Step 2: [Create OAuth credentials](https://developers.google.com/workspace/drive/api/quickstart/python#authorize_credentials_for_a_desktop_application). 

- Go to APIs & Services > Credentials.
- Click “+ Create credentials” > OAuth client ID.
- If prompted, configure the OAuth consent screen with "Audience: External".
- Select application type: "Desktop app".
- Create the application
- Download the credentials JSON and rename it to `google_drive_credentials.json`.

Step 3: Add test users.

- Go to OAuth consent screen > Test users.
- Add your email address.

Step 4: Edit configuration file.

- Edit `credentials_path` with your path to `google_drive_credentials.json`.
- Edit `path_id` with your source or target location. It can be obtained from the URL as follows:
    - Folder: `https://drive.google.com/drive/u/0/folders/1yucgL9WGgWZdM1TOuKkeghlPizuzMYb5` > folder id is `1yucgL9WGgWZdM1TOuKkeghlPizuzMYb5`.
    - File: `https://docs.google.com/document/d/1bfaMQ18_i56204VaQDVeAFpqEijJTgvurupdEDiaUQw/edit` > document id is `1bfaMQ18_i56204VaQDVeAFpqEijJTgvurupdEDiaUQw`.

Step 5: Authenticate via CLI.

- Run the CLI with your configuration file.
- A browser window will open for authentication and gerate a token file that will be save on the configured `token_path` and reused for next runs.



================================================
FILE: docs/usage/mcp.md
================================================
New AI trends focus on Agentic AI, an artificial intelligence system that can accomplish a specific goal with limited supervision.
Agents can act autonomously to understand, plan, and execute a specific task.

To address the integration problem, the [Model Context Protocol](https://modelcontextprotocol.io) (MCP) emerges as a popular standard for connecting AI applications to external tools.

## chonkie MCP

chonkie supports the development of AI agents by providing an MCP Server. It allows you to experiment with document processing in different MCP Clients. Adding [chonkie MCP](https://github.com/chonkie-project/chonkie-mcp) in your favorite client is usually as simple as adding the following entry in the configuration file:

```json
{
  "mcpServers": {
    "chonkie": {
      "command": "uvx",
      "args": [
        "--from=chonkie-mcp",
        "chonkie-mcp-server"
      ]
    }
  }
}
```

When using [Claude on your desktop](https://claude.ai/download), just edit the config file `claude_desktop_config.json` with the snippet above or the example provided [here](https://github.com/chonkie-project/chonkie-mcp/blob/main/docs/integrations/claude_desktop_config.json).

In **[LM Studio](https://lmstudio.ai/)**, edit the `mcp.json` file with the appropriate section or simply click on the button below for a direct install.

[![Add MCP Server chonkie to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-light.svg)](https://lmstudio.ai/install-mcp?name=chonkie&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLWZyb209ZG9jbGluZy1tY3AiLCJkb2NsaW5nLW1jcC1zZXJ2ZXIiXX0%3D)


chonkie MCP also provides tools specific for some applications and frameworks. See the [chonkie MCP](https://github.com/chonkie-project/chonkie-mcp) Server repository for more details. You will find examples of building agents powered by chonkie capabilities and leveraging frameworks like [LlamaIndex](https://www.llamaindex.ai/), [Llama Stack](https://github.com/llamastack/llama-stack), [Pydantic AI](https://ai.pydantic.dev/), or [smolagents](https://github.com/huggingface/smolagents).



================================================
FILE: docs/usage/supported_formats.md
================================================
chonkie can parse various documents formats into a unified representation (chonkie
Document), which it can export to different formats too — check out
[Architecture](../concepts/architecture.md) for more details.

Below you can find a listing of all supported input and output formats.

## Supported input formats

| Format | Description |
|--------|-------------|
| PDF | |
| DOCX, XLSX, PPTX | Default formats in MS Office 2007+, based on Office Open XML |
| Markdown | |
| AsciiDoc | Human-readable, plain-text markup language for structured technical content |
| HTML, XHTML | |
| CSV | |
| PNG, JPEG, TIFF, BMP, WEBP | Image formats |
| WebVTT | Web Video Text Tracks format for displaying timed text |

Schema-specific support:

| Format | Description |
|--------|-------------|
| USPTO XML | XML format followed by [USPTO](https://www.uspto.gov/patents) patents |
| JATS XML | XML format followed by [JATS](https://jats.nlm.nih.gov/) articles |
| chonkie JSON | JSON-serialized [chonkie Document](../concepts/chonkie_document.md) |

## Supported output formats

| Format | Description |
|--------|-------------|
| HTML | Both image embedding and referencing are supported |
| Markdown | |
| JSON | Lossless serialization of chonkie Document |
| Text | Plain text, i.e. without Markdown markers |
| [Doctags](https://arxiv.org/pdf/2503.11576) | Markup format for efficiently representing the full content and layout characteristics of a document |



================================================
FILE: docs/usage/vision_models.md
================================================

The `VlmPipeline` in chonkie allows you to convert documents end-to-end using a vision-language model.

chonkie supports vision-language models which output:

- DocTags (e.g. [Smolchonkie](https://huggingface.co/ds4sd/Smolchonkie-256M-preview)), the preferred choice
- Markdown
- HTML


For running chonkie using local models with the `VlmPipeline`:

=== "CLI"

    ```bash
    chonkie --pipeline vlm FILE
    ```

=== "Python"

    See also the example [minimal_vlm_pipeline.py](./../examples/minimal_vlm_pipeline.py).

    ```python
    from chonkie.datamodel.base_models import InputFormat
    from chonkie.document_converter import DocumentConverter, PdfFormatOption
    from chonkie.pipeline.vlm_pipeline import VlmPipeline

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=VlmPipeline,
            ),
        }
    )

    doc = converter.convert(source="FILE").document
    ```

## Available local models

By default, the vision-language models are running locally.
chonkie allows to choose between the Hugging Face [Transformers](https://github.com/huggingface/transformers) framework and the [MLX](https://github.com/Blaizzy/mlx-vlm) (for Apple devices with MPS acceleration) one.

The following table reports the models currently available out-of-the-box.

| Model instance | Model | Framework | Device | Num pages | Inference time (sec) |
| ---------------|------ | --------- | ------ | --------- | ---------------------|
| `vlm_model_specs.GRANITEchonkie_TRANSFORMERS` | [ibm-granite/granite-chonkie-258M](https://huggingface.co/ibm-granite/granite-chonkie-258M) | `Transformers/AutoModelForVision2Seq` | MPS | 1 |  - |
| `vlm_model_specs.GRANITEchonkie_MLX` | [ibm-granite/granite-chonkie-258M-mlx-bf16](https://huggingface.co/ibm-granite/granite-chonkie-258M-mlx-bf16) | `MLX`| MPS | 1 |    - |
| `vlm_model_specs.SMOLchonkie_TRANSFORMERS` | [ds4sd/Smolchonkie-256M-preview](https://huggingface.co/ds4sd/Smolchonkie-256M-preview) | `Transformers/AutoModelForVision2Seq` | MPS | 1 |  102.212 |
| `vlm_model_specs.SMOLchonkie_MLX` | [ds4sd/Smolchonkie-256M-preview-mlx-bf16](https://huggingface.co/ds4sd/Smolchonkie-256M-preview-mlx-bf16) | `MLX`| MPS | 1 |    6.15453 |
| `vlm_model_specs.QWEN25_VL_3B_MLX` | [mlx-community/Qwen2.5-VL-3B-Instruct-bf16](https://huggingface.co/mlx-community/Qwen2.5-VL-3B-Instruct-bf16)  |  `MLX`| MPS | 1 |   23.4951 |
| `vlm_model_specs.PIXTRAL_12B_MLX` | [mlx-community/pixtral-12b-bf16](https://huggingface.co/mlx-community/pixtral-12b-bf16) |  `MLX` | MPS | 1 |  308.856 |
| `vlm_model_specs.GEMMA3_12B_MLX` | [mlx-community/gemma-3-12b-it-bf16](https://huggingface.co/mlx-community/gemma-3-12b-it-bf16) |  `MLX` | MPS | 1 |  378.486 |
| `vlm_model_specs.GRANITE_VISION_TRANSFORMERS` | [ibm-granite/granite-vision-3.2-2b](https://huggingface.co/ibm-granite/granite-vision-3.2-2b) | `Transformers/AutoModelForVision2Seq` | MPS | 1 |  104.75 |
| `vlm_model_specs.PHI4_TRANSFORMERS` | [microsoft/Phi-4-multimodal-instruct](https://huggingface.co/microsoft/Phi-4-multimodal-instruct) | `Transformers/AutoModelForCasualLM` | CPU | 1 | 1175.67 |
| `vlm_model_specs.PIXTRAL_12B_TRANSFORMERS` | [mistral-community/pixtral-12b](https://huggingface.co/mistral-community/pixtral-12b) | `Transformers/AutoModelForVision2Seq` | CPU | 1 | 1828.21 |

_Inference time is computed on a Macbook M3 Max using the example page `tests/data/pdf/2305.03393v1-pg9.pdf`. The comparison is done with the example [compare_vlm_models.py](../examples/compare_vlm_models.py)._

For choosing the model, the code snippet above can be extended as follow

```python
from chonkie.datamodel.base_models import InputFormat
from chonkie.document_converter import DocumentConverter, PdfFormatOption
from chonkie.pipeline.vlm_pipeline import VlmPipeline
from chonkie.datamodel.pipeline_options import (
    VlmPipelineOptions,
)
from chonkie.datamodel import vlm_model_specs

pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.SMOLchonkie_MLX,  # <-- change the model here
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=VlmPipeline,
            pipeline_options=pipeline_options,
        ),
    }
)

doc = converter.convert(source="FILE").document
```

### Other models

Other models can be configured by directly providing the Hugging Face `repo_id`, the prompt and a few more options.

For example:

```python
from chonkie.datamodel.pipeline_options_vlm_model import InlineVlmOptions, InferenceFramework, TransformersModelType

pipeline_options = VlmPipelineOptions(
    vlm_options=InlineVlmOptions(
        repo_id="ibm-granite/granite-vision-3.2-2b",
        prompt="Convert this page to markdown. Do not miss any text and only output the bare markdown!",
        response_format=ResponseFormat.MARKDOWN,
        inference_framework=InferenceFramework.TRANSFORMERS,
        transformers_model_type=TransformersModelType.AUTOMODEL_VISION2SEQ,
        supported_devices=[
            AcceleratorDevice.CPU,
            AcceleratorDevice.CUDA,
            AcceleratorDevice.MPS,
        ],
        scale=2.0,
        temperature=0.0,
    )
)
```


## Remote models

Additionally to local models, the `VlmPipeline` allows to offload the inference to a remote service hosting the models.
Many remote inference services are provided, the key requirement is to offer an OpenAI-compatible API. This includes vLLM, Ollama, etc.

More examples on how to connect with the remote inference services can be found in the following examples:

- [vlm_pipeline_api_model.py](../examples/vlm_pipeline_api_model.py)


