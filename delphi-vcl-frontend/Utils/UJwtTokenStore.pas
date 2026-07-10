unit UJwtTokenStore;

interface

type
  TJwtTokenStore = class
  private
    class var FToken: string;
  public
    class procedure SetToken(const AToken: string); static;
    class function GetToken: string; static;
    class function HasToken: Boolean; static;
    class procedure Clear; static;
  end;

implementation

uses
  System.SysUtils;

class procedure TJwtTokenStore.Clear;
begin
  FToken := '';
end;

class function TJwtTokenStore.GetToken: string;
begin
  Result := FToken;
end;

class function TJwtTokenStore.HasToken: Boolean;
begin
  Result := FToken <> '';
end;

class procedure TJwtTokenStore.SetToken(const AToken: string);
begin
  FToken := Trim(AToken);
end;

end.
