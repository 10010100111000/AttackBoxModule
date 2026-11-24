FROM ruby:3.1-slim-bookworm AS runtime
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends wkhtmltopdf ca-certificates curl; \
    rm -rf /var/lib/apt/lists/*; \
    gem install --no-document pdfkit -v 0.8.6; \
    gem install --no-document sinatra -v 2.2.4; \
    gem install --no-document webrick -v 1.9.1; \
    useradd --system --create-home --home-dir /home/ruby --shell /usr/sbin/nologin ruby; \
    mkdir -p /app /run/precious /home/ruby; \
    chown -R ruby:ruby /run/precious /home/ruby
WORKDIR /app
COPY site/ /app/
COPY scripts/start.sh /usr/local/bin/precious-start
COPY flags/user.txt /home/ruby/user.txt
RUN chmod 0755 /usr/local/bin/precious-start && \
    chown ruby:ruby /home/ruby/user.txt && chmod 0400 /home/ruby/user.txt && \
    ruby -c /app/app.rb
EXPOSE 8080
HEALTHCHECK --interval=20s --timeout=5s --start-period=25s --retries=3 \
  CMD ["curl","-fsS","http://127.0.0.1:8080/health"]
ENTRYPOINT ["/usr/local/bin/precious-start"]
