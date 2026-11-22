# syntax=docker/dockerfile:1.7
# Compact Photobomb reconstruction: Ruby/Sinatra + Nginx + ImageMagick + SSH + sudo.
FROM ruby:2.7.8-alpine3.16 AS ruby-deps
ENV GEM_HOME=/usr/local/bundle
ENV PATH=/usr/local/bundle/bin:$PATH
RUN gem install --no-document sinatra -v 2.0.8.1 \
 && gem install --no-document webrick -v 1.6.1

FROM ruby:2.7.8-alpine3.16 AS runtime
ENV GEM_HOME=/usr/local/bundle
ENV PATH=/usr/local/bundle/bin:$PATH
RUN apk add --no-cache nginx imagemagick openssh sudo bash su-exec openssl \
 && addgroup -g 1000 wizard \
 && adduser -D -u 1000 -G wizard -h /home/wizard -s /bin/bash wizard \
 && mkdir -p /run/nginx /run/sshd /home/wizard/photobomb/source_images \
      /home/wizard/photobomb/resized_images /home/wizard/photobomb/log \
      /home/wizard/photobomb/public/ui_images \
 && rm -f /etc/nginx/http.d/default.conf
COPY --from=ruby-deps /usr/local/bundle /usr/local/bundle
WORKDIR /home/wizard/photobomb
COPY app/server.rb ./server.rb
COPY app/public/ ./public/
COPY config/nginx.conf /etc/nginx/http.d/default.conf
COPY config/photobomb.htpasswd /etc/nginx/photobomb.htpasswd
COPY config/sshd_config /etc/ssh/sshd_config
COPY scripts/cleanup.sh /opt/cleanup.sh
COPY scripts/opt.bashrc /opt/.bashrc
COPY scripts/entrypoint.sh /usr/local/bin/photobomb-entrypoint
COPY scripts/healthcheck.rb /usr/local/bin/photobomb-healthcheck.rb
COPY flags/user.txt /home/wizard/user.txt
COPY flags/root.txt /root/root.txt
# Recreate the documented APR1 Basic Auth hash deterministically for Nginx.
RUN set -eux; hash=$(openssl passwd -apr1 -salt dnyF00ZD 'b0Mb!'); printf 'pH0t0:%s\n' "$hash" > /etc/nginx/photobomb.htpasswd
# Original high-resolution Unsplash files are not publicly distributed with
# the writeups. Generate tiny local JPG gallery assets with real ImageMagick.
RUN set -eux; \
    convert -size 480x320 gradient:'#1b2735-#607d8b' -quality 72 source_images/voicu-apostol-MWER49YaD-M-unsplash.jpg; \
    convert -size 480x320 gradient:'#243b55-#6a8caf' -quality 72 source_images/masaaki-komori-NYFaNoiPf7A-unsplash.jpg; \
    convert -size 480x320 gradient:'#42275a-#734b6d' -quality 72 source_images/finn-whelen-DTfhsDIWNSg-unsplash.jpg; \
    convert -size 480x320 gradient:'#134e5e-#71b280' -quality 72 source_images/wolfgang-hasselmann-RLEgmd1O7gs-unsplash.jpg; \
    cp source_images/*.jpg public/ui_images/; \
    touch log/photobomb.log; \
    chown -R wizard:wizard /home/wizard/photobomb; \
    chmod 0644 /home/wizard/user.txt; \
    chmod 0600 /root/root.txt; \
    chown root:root /opt/cleanup.sh /opt/.bashrc; \
    chmod 0755 /opt/cleanup.sh; \
    chmod 0644 /opt/.bashrc; \
    chmod 0755 /usr/local/bin/photobomb-entrypoint /usr/local/bin/photobomb-healthcheck.rb; \
    chown root:nginx /etc/nginx/photobomb.htpasswd; \
    chmod 0640 /etc/nginx/photobomb.htpasswd; \
    printf '%s\n' 'wizard ALL=(root) SETENV: NOPASSWD: /opt/cleanup.sh' > /etc/sudoers.d/wizard; \
    chmod 0440 /etc/sudoers.d/wizard; \
    nginx -t; \
    visudo -cf /etc/sudoers
EXPOSE 22 80
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=20s --timeout=8s --start-period=25s --retries=3 \
  CMD ["ruby", "/usr/local/bin/photobomb-healthcheck.rb"]
ENTRYPOINT ["/usr/local/bin/photobomb-entrypoint"]
