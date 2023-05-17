# ClipBugBERT
Adapted model from ClipBERT
[Less is More: ClipBERT for Video-and-Language Learning via Sparse Sampling](https://arxiv.org/abs/2102.06183) 

## Seting up the Environment and dependencies 
1. Clone the project: 
        ``` git clone URL/to/repo ```
2. Create a virtual python environment and activate the venv
3. Nevigate to ClipBugBERT/docker directory.  Install the requirements.txt file.
         ``` pip install requirement.txt  ```
4. The ClipBert model uses "Apex" library which is not a torch library. Apex is a library developed by NVIDIA that enables mixed precision training in PyTorch. So if the requirement.txt installation fails to install "Apex" the manual installation will be required.
5. Installing Apex: 
    - Make sure you have CUDA installed on your system. You can check by running nvcc --version. If it's not installed, you can follow the instructions on the official NVIDIA website to install it.
    - Clone the Apex repository
    - install Apex by following cmd
         ``` pip3 install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" ./" ```
6.  If the version of CUDA used to compile PyTorch binaries and the version of CUDA you are using to compile Apex are not the same then this may cause issues during the installation process. 

If all the installation is done after successfully installing the requirements.txt then the ClipBert model can be run. 


## Data Preprocessing
ClipBERT takes raw video and text as inputs, there is no need to do feature extraction. 
However, to improve data loading speed, we use LMDB to store the raw image and video files. 
You can use the following script to convert a list of videos with file extensions `mp4` and `avi` into LMDB:
    
```bash
# outside the container
python src/preprocessing/file2lmdb.py \
    --data_root /path/to/videos \
    --lmdb_save_dir /path/to/save/lmdb \
    --ext avi mp4 \
    --file_type video 
```

For images, use appropriate file extensions for `--ext` and `--file_type image`. 
Text annotation files are reorganized into `jsonl` files, 
see example preprocessed files downloaded by the scripts in [scripts/](scripts).  

### General

1. Create a folder that stores pretrained models, all the data, and results.
    ```bash
    PATH_TO_STORAGE=/path/to/your/data/
    mkdir -p $PATH_TO_STORAGE/txt_db  # annotations
    mkdir -p $PATH_TO_STORAGE/vis_db  # image and video 
    mkdir -p $PATH_TO_STORAGE/finetune  # finetuning results
    mkdir -p $PATH_TO_STORAGE/pretrained  # pretrained models
    ```

2. Download pretrained models.

    Our e2e pretrained ClipBERT model (849MB), can be downloaded with the following command.
    ```bash
    bash scripts/download_pretrained.sh $PATH_TO_STORAGE
    ```
    This pretrained model can be used for finetuning on video-text tasks and image-text tasks.
    For your convenience, this script will also download `bert-base-uncased` and `grid-feat-vqa` 
    model weights, which are used as initialization for pretraining. 

#### Image Question Answering (VQA)
1. Finetuning
    ```bash
    python src/tasks/run_vqa.py \
        --config src/configs/rico_vqa_base_resnet50.json \
        --output_dir $OUTPUT_DIR
    ```
    Note: Makesure to use a directory outside the project as the _OUTPUT_DIR_

3. Inference
    ```bash
    # inside the container
    python src/tasks/run_vqa.py \
      --do_inference 1 --output_dir $OUTPUT_DIR \
      --inference_split val --inference_model_step $STEP \
      --inference_txt_db $TXT_DB \
      --inference_img_db $IMG_DB \
      --inference_batch_size 64
    ```    

    $STEP is an integer, which tells the script to use the checkpoint $OUTPUT_DIR/ckpt/model_step_$STEP.pt for inference. $TXT_DB and $IMG_DB are path to annotation file and video data. You can use TXT_DB=/txt/rico/vqa_k_test.jsonl and IMG_DB=/img/rico for inference on RICO QA test split.

    #### Video Question Answering
    1. Finetuning. 
        ```bash
        # inside the container
        python src/tasks/run_video_qa.py \
            --config $CONFIG_PATH \
            --output_dir $OUTPUT_DIR
        ```
        `$CONFIG_PATH` should be set to one of the .json config files available at [src/configs](src/configs) 
        contains the substring `_qa`. For example, you can use `src/configs/tango_qa_base_resnet50.json` 
        for MSRVTT-QA.

    2. Run inference.
    ```bash
    python src/tasks/run_video_qa.py \
      --do_inference 1 --output_dir $OUTPUT_DIR \
      --inference_split val --inference_model_step $STEP \
      --inference_txt_db $TXT_DB \
      --inference_img_db $IMG_DB --inference_batch_size 64 \
      --inference_n_clips $INFERENCE_N_CLIPS
      --ans2label_path $ANS_TO_LABEL
    ```
   `$STEP` is an integer, which tells the script to use the checkpoint 
   `$OUTPUT_DIR/ckpt/model_step_$STEP.pt` for inference.
   `$TXT_DB` and `$IMG_DB` are path to annotation file and video data. You can use
   `TXT_DB=/txt/tango/test.jsonl` and 
   `IMG_DB=/img/tango` for inference on TANGO QA test split.
   `$ANS_TO_LABEL` path to ans2label.json file
   
    The results will be written under `$OUTPUT_DIR`. You can use different `$INFERENCE_N_CLIPS` 
    for inference, such as 1 or 16. Using more clips will have a large impact 
    on inference speed and memory usage. You may want to use smaller batch sizes if larger 
    values are set.    


