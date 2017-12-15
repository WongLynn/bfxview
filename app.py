from bfxview import create_app

app = create_app('/Users/fangfang/Documents/repo/bfxview/test.cfg')

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)