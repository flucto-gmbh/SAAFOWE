# This script creates a report PDF and saves it in the "reports" folder.


rel_path = '../tests'
file_name = 'report.pdf'

def run():
    # Dummy stuff
    # Thanks to: https://towardsdatascience.com/creating-pdf-files-with-python-ad3ccadfae0f
    #python -m pip install fpdf # installation
    from fpdf import FPDF  # fpdf class
    import lorem
    class PDF(FPDF):
        def lines(self):
            self.rect(5.0, 5.0, 200.0,287.0)
        def titles(self):
            self.set_xy(0.0,0.0)
            self.set_font('Arial', 'B', 16)
            self.set_text_color(220, 50, 50)
            self.cell(w=210.0, h=40.0, align='C', txt="24-hour report", border=0)
        def dummytext(self):   
            self.set_font('Arial', style='', size=10)
            self.set_text_color(0, 0, 0)
            p = lorem.paragraph()
            for i in range(3):
                self.set_xy(10, 90 + (i + 1) * 50)
                self.multi_cell(w=190.0, h=5.0, align='L', txt=p, border=0, fill=False)
        def imagex(self):
                self.set_xy(70, 40)
                self.image('../tests/imu.jpg',  link='', type='', w=int(644/10), h=int(759/10))
            
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.lines()
    pdf.titles()
    pdf.imagex()
    pdf.dummytext()

    full_name = rel_path + '/' + file_name
    pdf.output(full_name, 'F')

    print('Successfully created a PDF report.')

if __name__ == "__main__":
    run()
