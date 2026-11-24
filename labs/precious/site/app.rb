# frozen_string_literal: true
require 'sinatra'
require 'pdfkit'
require 'securerandom'
require 'uri'

set :bind, '0.0.0.0'
set :port, 8080
set :server, :webrick
set :environment, :production
set :show_exceptions, false

get '/health' do
  content_type 'text/plain'
  'ok'
end

get '/' do
  content_type 'text/html'
  File.read(File.join(__dir__, 'index.html'))
end

post '/' do
  input = params['url'].to_s
  unless input.start_with?('http://', 'https://')
    status 400
    return 'You should provide a valid URL!'
  end

  begin
    # Genuine vulnerable PDFKit v0.8.6. Do not substitute wkhtmltopdf shell
    # invocation or a simulated endpoint: PDFKit constructs its own command.
    kit = PDFKit.new(input, page_size: 'Letter')
    pdf = kit.to_pdf
    content_type 'application/pdf'
    headers 'Content-Disposition' => "attachment; filename=\"#{SecureRandom.hex(8)}.pdf\""
    body pdf
  rescue StandardError
    status 422
    'Cannot load remote URL!'
  end
end
