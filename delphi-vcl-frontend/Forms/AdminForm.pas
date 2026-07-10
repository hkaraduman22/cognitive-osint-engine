unit AdminForm;

interface

uses
  Winapi.Windows,
  Winapi.Messages,
  System.SysUtils,
  System.Variants,
  System.Classes,
  Vcl.Graphics,
  Vcl.Controls,
  Vcl.Forms,
  Vcl.Dialogs,
  Vcl.StdCtrls;

type
  TFrmAdmin = class(TForm)
    LblTitle: TLabel;
    BtnLoadUsers: TButton;
    BtnLoadLogs: TButton;
    BtnClose: TButton;
    MemoUsers: TMemo;
    MemoLogs: TMemo;
    LblUsers: TLabel;
    LblLogs: TLabel;
    LblStatus: TLabel;
    procedure BtnLoadUsersClick(Sender: TObject);
    procedure BtnLoadLogsClick(Sender: TObject);
    procedure BtnCloseClick(Sender: TObject);
  private
    procedure RenderUsers;
    procedure RenderLogs;
  public
    { Public declarations }
  end;

var
  FrmAdmin: TFrmAdmin;

implementation

{$R *.dfm}

uses
  UAdminService,
  UJwtTokenStore;

procedure TFrmAdmin.BtnCloseClick(Sender: TObject);
begin
  Close;
end;

procedure TFrmAdmin.BtnLoadLogsClick(Sender: TObject);
begin
  RenderLogs;
end;

procedure TFrmAdmin.BtnLoadUsersClick(Sender: TObject);
begin
  RenderUsers;
end;

procedure TFrmAdmin.RenderLogs;
var
  LService: TAdminService;
  LData: TAdminLogItems;
  I: Integer;
begin
  LblStatus.Caption := 'Admin logs yukleniyor...';
  MemoLogs.Clear;

  LService := TAdminService.Create;
  try
    LData := LService.GetLogs(TJwtTokenStore.GetToken);
    if Length(LData) = 0 then
      MemoLogs.Lines.Add('Log kaydi bulunamadi.')
    else
    begin
      for I := 0 to High(LData) do
      begin
        MemoLogs.Lines.Add('ID: ' + IntToStr(LData[I].Id));
        MemoLogs.Lines.Add('User ID: ' + IntToStr(LData[I].UserId));
        MemoLogs.Lines.Add('Query: ' + LData[I].Query);
        MemoLogs.Lines.Add('Status: ' + LData[I].Status);
        MemoLogs.Lines.Add('Message: ' + LData[I].MessageText);
        MemoLogs.Lines.Add('Created At: ' + LData[I].CreatedAt);
        MemoLogs.Lines.Add('----------------------------------------');
      end;
    end;

    LblStatus.Caption := 'Logs toplam: ' + IntToStr(Length(LData));
  finally
    LService.Free;
  end;
end;

procedure TFrmAdmin.RenderUsers;
var
  LService: TAdminService;
  LData: TAdminUserItems;
  I: Integer;
  LAdminText: string;
begin
  LblStatus.Caption := 'Admin users yukleniyor...';
  MemoUsers.Clear;

  LService := TAdminService.Create;
  try
    LData := LService.GetUsers(TJwtTokenStore.GetToken);
    if Length(LData) = 0 then
      MemoUsers.Lines.Add('Kullanici kaydi bulunamadi.')
    else
    begin
      for I := 0 to High(LData) do
      begin
        if LData[I].IsAdmin then
          LAdminText := 'true'
        else
          LAdminText := 'false';

        MemoUsers.Lines.Add('ID: ' + IntToStr(LData[I].Id));
        MemoUsers.Lines.Add('Username: ' + LData[I].Username);
        MemoUsers.Lines.Add('Is Admin: ' + LAdminText);
        MemoUsers.Lines.Add('Created At: ' + LData[I].CreatedAt);
        MemoUsers.Lines.Add('----------------------------------------');
      end;
    end;

    LblStatus.Caption := 'Users toplam: ' + IntToStr(Length(LData));
  finally
    LService.Free;
  end;
end;

end.
