require 'net/http'
require 'uri'
require 'socket'

root = Net::HTTP.get_response(URI('http://127.0.0.1/'))
raise 'root page failed' unless root.code == '200' && root.body.include?('Photobomb')
printer = Net::HTTP::Get.new(URI('http://127.0.0.1/printer'))
printer.basic_auth('pH0t0', 'b0Mb!')
response = Net::HTTP.start('127.0.0.1', 80) { |http| http.request(printer) }
raise 'printer auth failed' unless response.code == '200' && response.body.include?('Select an image')
socket = TCPSocket.new('127.0.0.1', 22)
banner = socket.gets.to_s
socket.close
raise 'SSH is not ready' unless banner.start_with?('SSH-2.0-')
