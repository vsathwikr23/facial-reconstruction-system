import os
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
from nbformat import read, write
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))

def execute_notebook(notebook_path, params):
    for key, value in params.items():
        os.environ[key.upper()] = str(value)

    with open(notebook_path) as f:
        nb = read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

    try:
        ep.preprocess(nb, {'metadata': {'path': base_dir}})
    except CellExecutionError as e:
        print(f"Error executing the notebook: {e}")
        raise

    output_path = os.getenv('OUTPUT_PATH')
    return output_path

ALLOWED_EXTENSIONS = ['mp4']
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        file1 = request.files.get('image1')
        file2 = request.files.get('image2')
        method = request.form.get('method')

        if file1 and file2 and file1.filename and file2.filename:
            image_dir = os.path.join(base_dir, 'static', 'images')
            video_dir = os.path.join(base_dir, 'static', 'videos')
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            if not os.path.exists(video_dir):
                os.makedirs(video_dir)
            

            image1_path = os.path.join(image_dir, file1.filename)
            image2_path = os.path.join(image_dir, file2.filename)

            file1.save(image1_path)
            file2.save(image2_path)

            if method == 'video':
                notebook_path = 'DIP project affine transform.ipynb'
                output_path = os.path.join(video_dir, 'output_video.mp4')
            elif method == 'Feature':
                notebook_path = 'feature_based_morphing.ipynb'
                output_path = os.path.join(video_dir, 'output_video.mp4')
            elif method == 'gaussian':
                notebook_path = 'gaussian_image.ipynb'
                output_path = os.path.join(image_dir, 'output_image.png')
            elif method == 'Linear':
                notebook_path = 'Linear_Interpolation_with_triangularsubdivision.ipynb'
                output_path = os.path.join(image_dir, 'output_image.png')
            elif method == 'Weighted_Average':
                notebook_path = 'Improved_weighted_averaging_technique.ipynb'
                output_path = os.path.join(image_dir, 'output_image.png')

            execute_notebook(notebook_path, {
                'image1_path': image1_path,
                'image2_path': image2_path,
                'output_path': output_path
            })
            
            if method == 'video' or method == 'Feature':
                output_video_url = url_for('static', filename=f'videos/{os.path.basename(output_path)}')
                return render_template('upload.html', output_video_url=output_video_url)
            else:
                output_image_url = url_for('static', filename=f'images/{os.path.basename(output_path)}')
                return render_template('upload.html', output_image_url=output_image_url)


        return redirect(request.url)
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(port=3000, debug=True)
